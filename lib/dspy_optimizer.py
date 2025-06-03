import dspy
import mlflow
from typing import List

from lib.dspy_metrics import weighted_metric, comprehensive_evaluation


def train_model(examples: List[dspy.Example]) -> dspy.Module:
    """Train optimized classifier with improved metrics."""
    from lib.dspy_classifier import IATIClassifier
    
    # Split data
    split_idx = int(len(examples) * 0.8)
    trainset = examples[:split_idx]
    devset = examples[split_idx:]
    
    # Create classifier
    classifier = dspy.ChainOfThought(IATIClassifier)
    
    # Optimize using weighted metric
    optimizer = dspy.MIPROv2(
        metric=weighted_metric,  # Use weighted metric for optimization
        auto="light",
    )
    
    with mlflow.start_run():
        optimized = optimizer.compile(
            classifier,
            trainset=trainset,
            max_bootstrapped_demos=3,
            max_labeled_demos=5,
            requires_permission_to_run=False,
        )
        
        # Comprehensive evaluation
        main_score, field_scores = comprehensive_evaluation(optimized, devset)
        
        print(f"Main weighted score: {main_score:.3f}")
        for field, score in field_scores.items():
            print(f"{field}: {score:.3f}")
    
    return optimized


def prepare_examples(activities: List[dict]) -> List[dspy.Example]:
    """Convert activities to DSPy examples."""
    from definitions import NARRATIVE_FIELDS
    
    examples = []
    llm_fields = [
        "llm_ref_group",
        "llm_target_population",
        "llm_ref_setting",
        "llm_geographic_focus",
        "llm_nexus",
        "llm_funding_org",
        "llm_implementing_org",
    ]

    for activity in activities:
        if not activity.get("title_narrative"):
            continue

        example_kwargs = {
            **{field: activity.get(field, "") for field in NARRATIVE_FIELDS},
            **{field: activity.get(field, []) for field in llm_fields},
        }

        example = dspy.Example(**example_kwargs).with_inputs(*NARRATIVE_FIELDS)
        examples.append(example)
    return examples
