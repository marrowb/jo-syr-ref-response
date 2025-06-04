import os
import sys
from datetime import datetime
from pathlib import Path
import asyncio

import dspy

from definitions import DSPY_CONFIG, GEMINI_API_KEY, NARRATIVE_FIELDS, ROOT_DIR
from lib.dspy_classifier import generate_labels, smart_sample
from lib.dspy_optimizer import prepare_examples, train_model
from lib.dspy_batch_classify import label_all_activities_async
from lib.util_file import read_json, write_json
from lib.util_mlfow import MLflowServerManager, setup_mlflow_tracking


def setup_dspy_config():
    """Configure DSPy with the specified model."""
    task_model = dspy.LM(
        DSPY_CONFIG["task_model"], api_key=GEMINI_API_KEY, max_tokens=4000
    )
    strong_model = dspy.LM(
        DSPY_CONFIG["strong_model"], api_key=GEMINI_API_KEY, max_tokens=4000
    )
    dspy.configure(lm=task_model)


def build_sample_for_labeling():
    """Generate initial sample for human labeling."""
    print("Building sample for labeling...")
    activities_data = read_json("./data/iati/jordan_activities_narratives.json")
    sampled = smart_sample(activities_data, DSPY_CONFIG["sample_size"])
    print(f"Sampled {len(sampled)} activities")

    initial_labels = generate_labels(sampled, DSPY_CONFIG["strong_model"])
    write_json(initial_labels, "./data/training_pre_human.json")
    print("Sample saved to ./data/training_pre_human.json")


def train_classification_model():
    """Train the classification model on labeled data."""
    print("Training classification model...")

    labeled_data_path = os.path.join(
        ROOT_DIR, "data", "iati", "model", "jordan_activities_labeled.json"
    )

    if not os.path.exists(labeled_data_path):
        print(f"Error: Labeled data not found at {labeled_data_path}", file=sys.stderr)
        return None

    labeled_data = read_json(labeled_data_path)
    examples = prepare_examples(labeled_data)

    print(f"Training on {len(examples)} examples...")
    trained_model = train_model(examples)

    score = str(trained_model.score).split(".")[0]
    time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    model_path = os.path.join(ROOT_DIR, "models", f"aid_classifier_{score}_{time}.json")

    trained_model.save(model_path)
    print(f"Model saved to {model_path}")

    return trained_model


def label_all_activities(model) -> None:
    """Label all activities"""
    activities_path = os.path.join(
        ROOT_DIR, "data", "iati", "jordan_activities_narratives.json"
    )
    activities_data = read_json(activities_path)
    # Async loops
    results = []
    for activity in activities_data:
        narratives = [activity.get(k) for k in activity.keys() if k in NARRATIVE_FIELDS]
        pred = model(*narratives)
        activity_copy = activity.copy()
        #     activity_copy.update({field: getattr(pred, field) for field in
        #                          ['llm_ref_group', 'llm_target_population', etc...]})
        results.append(activity_copy)
    write_json(
        results,
        os.path.join(ROOT_DIR, "data", "iati", "all_activities_classified.json"),
    )


def load_saved_model(model_path: str):
    """Load a saved DSPy model from JSON format."""
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")
    
    from lib.dspy_classifier import IATIClassifier
    classifier = dspy.ChainOfThought(IATIClassifier)
    classifier.load(model_path)
    return classifier


async def batch_classify(model_path: str = None, num_activities: int = None, batch_size: int = 50):
    """Run batch classification with timestamp-based output folder."""
    
    # Create timestamped output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(ROOT_DIR) / "data" / "iati" / "batch-classify" / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load model
    if model_path:
        model = load_saved_model(model_path)
        print(f"Loaded model from: {model_path}")
    else:
        # Train new model
        labeled_data = read_json(os.path.join(ROOT_DIR, "data", "iati", "model", "jordan_activities_labeled.json"))
        examples = prepare_examples(labeled_data)
        model = train_model(examples)
        print("Trained new model")
    
    # Prepare input data
    activities_path = os.path.join(ROOT_DIR, "data", "iati", "jordan_activities_narratives.json")
    activities = read_json(activities_path)
    
    if num_activities:
        activities = activities[:num_activities]
        print(f"Processing subset: {num_activities} activities")
    
    # Create subset file in output directory
    subset_path = output_dir / "input_activities.json"
    write_json(activities, str(subset_path))
    
    # Run classification with custom paths
    await label_all_activities_async(
        model=model, 
        input_path=str(subset_path), 
        output_dir=str(output_dir), 
        batch_size=batch_size
    )
    
    print(f"Results saved to: {output_dir}")


def main():
    """Main execution pipeline."""
    print("Starting DSPy Model Pipeline...")

    # 1. Start MLflow server
    server = MLflowServerManager()
    if not server.start():
        print("Failed to start MLflow server. Exiting.", file=sys.stderr)
        sys.exit(1)

    # 2. Setup tracking and configuration
    # experiment_name = f"dspy-aid-activity-classification_{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}"
    setup_mlflow_tracking("dspy-aid-activity-classification")
    setup_dspy_config()

    # 3. Choose operation:
    # build_sample_for_labeling()
    # train_classification_model()
    
    # Test with 100 activities, batch size 50
    asyncio.run(batch_classify(
        model_path="models/aid_classifier_75_2024-12-19_14:30:15.json",  # Your model path
        num_activities=100,
        batch_size=50
    ))


if __name__ == "__main__":
    main()
