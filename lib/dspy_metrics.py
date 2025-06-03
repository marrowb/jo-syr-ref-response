import dspy
import mlflow
from typing import List


def weighted_metric(example, prediction, trace=None) -> float:
    """Weighted metric prioritizing critical fields."""
    
    # Define field weights based on importance
    field_weights = {
        "llm_ref_group": 3.0,           # Critical - refugee identification
        "llm_target_population": 3.0,   # Critical - who is served
        "llm_nexus": 2.0,              # Important - humanitarian vs development
        "llm_ref_setting": 1.5,        # Moderately important
        "llm_geographic_focus": 1.0,    # Nice to have
        "llm_funding_org": 0.5,        # Less critical
        "llm_implementing_org": 0.5,   # Less critical
    }
    
    total_weighted_score = 0
    total_weight = 0
    
    for field, weight in field_weights.items():
        if hasattr(example, field) and hasattr(prediction, field):
            expected = set(getattr(example, field, []))
            predicted = set(getattr(prediction, field, []))
            
            # Calculate field score
            if len(expected) == 0 and len(predicted) == 0:
                score = 1.0
            elif len(expected) == 0 or len(predicted) == 0:
                score = 0.0
            else:
                intersection = len(expected.intersection(predicted))
                union = len(expected.union(predicted))
                score = intersection / union if union > 0 else 0.0
            
            total_weighted_score += score * weight
            total_weight += weight
    
    return total_weighted_score / total_weight if total_weight > 0 else 0.0


def simple_metric(example, prediction, trace=None) -> float:
    """Simple overall accuracy metric."""
    total_score = 0
    total_fields = 0

    fields = [
        "llm_ref_group",
        "llm_target_population",
        "llm_ref_setting",
        "llm_geographic_focus",
        "llm_nexus",
        "llm_funding_org",
        "llm_implementing_org",
    ]

    for field in fields:
        if hasattr(example, field) and hasattr(prediction, field):
            expected = set(getattr(example, field, []))
            predicted = set(getattr(prediction, field, []))

            if len(expected) == 0 and len(predicted) == 0:
                score = 1.0
            elif len(expected) == 0 or len(predicted) == 0:
                score = 0.0
            else:
                intersection = len(expected.intersection(predicted))
                union = len(expected.union(predicted))
                score = intersection / union if union > 0 else 0.0

            total_score += score
            total_fields += 1

    return total_score / total_fields if total_fields > 0 else 0.0


def create_field_specific_metrics():
    """Create individual metrics for each field."""
    
    def make_field_metric(field_name):
        def field_metric(example, prediction, trace=None):
            if hasattr(example, field_name) and hasattr(prediction, field_name):
                expected = set(getattr(example, field_name, []))
                predicted = set(getattr(prediction, field_name, []))
                
                if len(expected) == 0 and len(predicted) == 0:
                    return 1.0
                elif len(expected) == 0 or len(predicted) == 0:
                    return 0.0
                else:
                    intersection = len(expected.intersection(predicted))
                    union = len(expected.union(predicted))
                    return intersection / union if union > 0 else 0.0
            return 0.0
        
        field_metric.__name__ = f"{field_name}_metric"
        return field_metric
    
    return {
        field: make_field_metric(field) 
        for field in ["llm_ref_group", "llm_target_population", "llm_nexus", 
                     "llm_ref_setting", "llm_geographic_focus", "llm_funding_org", 
                     "llm_implementing_org"]
    }


def comprehensive_evaluation(model, devset):
    """Evaluate with multiple metrics."""
    
    # Main weighted metric
    main_evaluator = dspy.Evaluate(devset=devset, metric=weighted_metric, num_threads=10)
    main_score = main_evaluator(model)
    
    # Field-specific metrics
    field_metrics = create_field_specific_metrics()
    field_scores = {}
    
    for field_name, metric_func in field_metrics.items():
        evaluator = dspy.Evaluate(devset=devset, metric=metric_func, num_threads=10)
        field_scores[field_name] = evaluator(model)
    
    # Log to MLflow
    mlflow.log_metric("main_weighted_score", main_score)
    for field_name, score in field_scores.items():
        mlflow.log_metric(f"score_{field_name}", score)
    
    return main_score, field_scores
