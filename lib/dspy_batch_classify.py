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
    """Robust async labeling with custom paths."""
    # TODO
    # Add a master classified list in iati/data
    # Create ids for the results based on being unique dicts

    # Use custom paths or defaults
    if not input_path:
        input_path = str(
            Path(ROOT_DIR) / "data" / "iati" / "jordan_activities_narratives.json"
        )
    if not output_dir:
        output_dir = str(Path(ROOT_DIR) / "data" / "iati")

    output_path = Path(output_dir) / "classified_results.json"
    progress_path = Path(output_dir) / "progress.json"
    errors_path = Path(output_dir) / "errors.json"

    # Load and filter
    progress = read_json(str(progress_path)) if progress_path.exists() else {"done": []}
    remaining = [
        a for a in activities if a.get("iati_identifier") not in progress["done"]
    ]

    print(f"Processing {len(remaining)}/{len(activities)} activities")

    # Process batches with conservative rate limiting
    semaphore = asyncio.Semaphore(10)  # Much lower concurrency

    for i in range(0, len(remaining), batch_size):
        batch = remaining[i : i + batch_size]

        # Concurrent classification
        tasks = [_classify_activity(model, activity, semaphore) for activity in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter successful results
        successful = []
        errors = []
        for activity, result in zip(batch, results):
            if isinstance(result, Exception):
                error = {"id": activity.get("iati_identifier"), "error": str(result)}
                errors.append(error)
                print(f"Error: {error}")
            elif _validate_result(result):
                successful.append(result)
                progress["done"].append(activity.get("iati_identifier"))
            else:
                error = {
                    "id": activity.get("iati_identifier"),
                    "error": "Invalid result format",
                }
                errors.append(error)
                print(f"Invalid result: {error}")

        # Save progress atomically
        _append_results(successful, output_path)
        if errors:
            _append_results(errors, errors_path)
        _save_progress(progress, progress_path)

        print(f"Batch {i//batch_size + 1}: {len(successful)}/{len(batch)} successful")
        await asyncio.sleep(2.0)  # Longer pause between batches


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


def _save_progress(progress, progress_path):
    """Atomic progress save."""
    progress["last_updated"] = datetime.now().isoformat()
    write_json(progress, str(progress_path))
