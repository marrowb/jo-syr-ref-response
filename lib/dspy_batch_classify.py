import asyncio
from datetime import datetime
from pathlib import Path

from definitions import NARRATIVE_FIELDS, ROOT_DIR
from lib.util_file import read_json, write_json


async def label_all_activities_async(
    model,
    activities,
    input_path: str = None,
    output_dir: str = None,
    batch_size: int = 50,
) -> None:
    """Robust async labeling with master progress tracking and retry logic."""
    
    # Master progress file in main data directory
    master_progress_path = Path(ROOT_DIR) / "data" / "iati" / "master_classification_progress.json"
    
    # Local output paths
    if not output_dir:
        output_dir = str(Path(ROOT_DIR) / "data" / "iati")
    
    output_path = Path(output_dir) / "classified_results.json"
    errors_path = Path(output_dir) / "errors.json"
    
    # Load master progress using unique_id
    master_progress = read_json(str(master_progress_path)) if master_progress_path.exists() else {"done": set()}
    if isinstance(master_progress["done"], list):
        master_progress["done"] = set(master_progress["done"])
    
    # Filter using unique_id instead of iati_identifier
    remaining = [a for a in activities if a.get("unique_id") not in master_progress["done"]]
    
    print(f"Processing {len(remaining)}/{len(activities)} activities")
    
    # Retry loop until all activities are classified
    max_retries = 3
    retry_count = 0
    
    while remaining and retry_count < max_retries:
        print(f"Retry attempt {retry_count + 1}/{max_retries}")
        
        semaphore = asyncio.Semaphore(10)
        
        for i in range(0, len(remaining), batch_size):
            batch = remaining[i:i + batch_size]
            
            tasks = [_classify_activity(model, activity, semaphore) for activity in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful = []
            errors = []
            
            for activity, result in zip(batch, results):
                if isinstance(result, Exception):
                    error = {"unique_id": activity.get("unique_id"), "error": str(result)}
                    errors.append(error)
                elif _validate_result(result):
                    successful.append(result)
                    master_progress["done"].add(activity.get("unique_id"))
                else:
                    error = {"unique_id": activity.get("unique_id"), "error": "Invalid result format"}
                    errors.append(error)
            
            # Save results and update master progress
            _append_results(successful, output_path)
            if errors:
                _append_results(errors, errors_path)
            
            # Save master progress (convert set to list for JSON)
            master_progress_save = {"done": list(master_progress["done"]), "last_updated": datetime.now().isoformat()}
            write_json(master_progress_save, str(master_progress_path))
            
            print(f"Batch {i//batch_size + 1}: {len(successful)}/{len(batch)} successful")
            await asyncio.sleep(2.0)
        
        # Update remaining list for next retry
        remaining = [a for a in activities if a.get("unique_id") not in master_progress["done"]]
        retry_count += 1
    
    # Final validation
    final_remaining = [a for a in activities if a.get("unique_id") not in master_progress["done"]]
    if final_remaining:
        print(f"WARNING: {len(final_remaining)} activities still unclassified after {max_retries} retries")
        unclassified_ids = [a.get("unique_id") for a in final_remaining]
        write_json({"unclassified_ids": unclassified_ids}, str(Path(output_dir) / "unclassified.json"))
    else:
        print("✅ All activities successfully classified!")


async def _classify_activity(model, activity, semaphore):
    """Classify single activity with proper error handling."""
    async with semaphore:
        try:
            narratives = {field: activity.get(field, "") for field in NARRATIVE_FIELDS}
            # Run model in thread pool since DSPy isn't async
            pred = await asyncio.to_thread(model, **narratives)

            result = activity.copy()
            pred_dict = pred.toDict() if hasattr(pred, "toDict") else pred.__dict__

            for field in [
                "llm_ref_group",
                "llm_target_population",
                "llm_ref_setting",
                "llm_geographic_focus",
                "llm_nexus",
                "llm_funding_org",
                "llm_implementing_org",
            ]:
                result[field] = pred_dict.get(field, [])

            result["classified_at"] = datetime.now().isoformat()
            return result

        except Exception as e:
            raise Exception(f"Classification failed: {str(e)}")


def _validate_result(result):
    """Ensure all classification fields exist as lists."""
    if not isinstance(result, dict):
        return False
    required = [
        "llm_ref_group",
        "llm_target_population",
        "llm_ref_setting",
        "llm_geographic_focus",
        "llm_nexus",
        "llm_funding_org",
        "llm_implementing_org",
    ]
    return all(isinstance(result.get(field), list) for field in required)


def _append_results(results, output_path):
    """Thread-safe append to file."""
    if not results:
        return
    existing = read_json(str(output_path)) if output_path.exists() else []
    existing.extend(results)
    write_json(existing, str(output_path))


