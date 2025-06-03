import os
import sys
from datetime import datetime

import dspy

from definitions import DATASTORE_FIELDS, DSPY_CONFIG, GEMINI_API_KEY, ROOT_DIR
from lib.dspy_classifier import *
from lib.util_file import read_json, write_json
from lib.util_mlfow import *


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

    # 3. Depending on what stage of model training you're at
    # Comment one of these out

    # build_sample_for_labeling()
    train_classification_model()


if __name__ == "__main__":
    main()
