from definitions import SECTOR_JSON_PATH
import dspy
from typing import List, Literal
import random
import json

class IATIClassifier(dspy.Signature):
    """Classify IATI aid activities based on narrative elements using IATI sector codes and refugee/humanitarian context."""
    
    title_narrative: str = dspy.InputField(desc="Project title")
    description_narrative: str = dspy.InputField(desc="Project description (may be empty)") 
    sector_narrative: str = dspy.InputField(desc="Sector-related narrative text")
    
    llm_ref_group: List[Literal["Syria", "Palestine", "Iraq", "Yemen", "Sudan", "Other", "mixed_or_unspecified_refugees"]] = dspy.OutputField(
        desc="""To identify specific refugee nationalities or a general reference to refugees explicitly mentioned in the narrative as beneficiaries or a significant focus of the project. This attribute does not include vulnerable host country nationals (e.g., Jordanians). Multiple values from ["Syria", "Palestine", "Iraq", "Yemen", "Sudan", "Other"] can be selected if the project targets multiple distinct refugee groups from this list. "Other" should be used if a specific refugee group not listed (e.g. Somali refugees) is explicitly mentioned. "mixed_or_unspecified_refugees" should be used if the narrative mentions refugees as beneficiaries or a focus but does not specify their nationality, or refers to multiple groups without detailing them individually in a way that allows for separate tagging. This value should not be used if specific nationalities are identifiable and can be tagged from the other options. This field should be an empty list [] only if the narrative or project has no mention or indication of focusing on or including refugees. If refugees are mentioned but no specific group is identifiable, ["mixed_or_unspecified_refugees"] should be used."""
    )
    
    llm_target_population: List[Literal["refugees", "host_communities", "general_population"]] = dspy.OutputField(
        desc="""To describe the broader categories of populations the project aims to serve, based on explicit mentions in the narrative. Multiple values can be selected. For instance, a project targeting both refugees and the communities that host them would have ["refugees", "host_communities"]. "refugees": Used when the project explicitly targets refugees (regardless of specific nationality, which is covered by llm_ref_group). "host_communities": Used when the project explicitly targets the communities accommodating refugees (e.g., vulnerable Jordanians in areas with high refugee presence). "general_population": Used when the project targets the wider population without a primary, explicit focus on refugee/host community dynamics, or if it's a national-level initiative not specifically disaggregated. If the target population is not clearly delineated in the narrative according to these categories, this field should be an empty list []."""
    )
    
    llm_ref_setting: List[Literal["camp", "urban", "rural"]] = dspy.OutputField(
        desc="""To describe the primary physical or social environment(s) where the project activities are stated to take place, particularly concerning vulnerable populations. Multiple values can be selected if activities explicitly occur across different setting types (e.g., ["camp", "urban"] if a project operates in both). "camp": Activities primarily occur within formal or informal refugee/IDP camp settings. "urban": Activities primarily occur in cities or towns. "rural": Activities primarily occur in countryside or non-urban settings. If the setting is not specified or unclear from the narrative, this field should be an empty list []."""
    )
    
    llm_geographic_focus: List[str] = dspy.OutputField(
        desc="""To list specific sub-national administrative areas, cities, or regions within the host country (e.g., Jordan) that are explicitly mentioned in the narrative as locations for project activities. Extracted names of locations (e.g., "Amman", "Zarka", "Irbid", "Mafraq governorate", "northern Jordan"). The value "national" can be used if the project is explicitly described as having a nationwide scope. If only the country name (e.g., "Jordan") is mentioned without further sub-national detail, and the scope isn't explicitly "national", then the country name can be used. If no specific sub-national locations, "national" scope, or country-level mention is present, this field should be an empty list []."""
    )
    
    llm_nexus: List[Literal["humanitarian", "development"]] = dspy.OutputField(
        desc="""To categorize the project's primary aim(s) along the humanitarian-development spectrum based on its narrative description. Multiple values can be selected if the project clearly and substantially integrates both humanitarian and development objectives and approaches (e.g., ["humanitarian", "development"]). "humanitarian": The project primarily focuses on saving lives, alleviating suffering, and maintaining human dignity during and in the aftermath of crises. It seeks to mitigate harms faced by vulnerable populations in the present. "development": The project primarily focuses on addressing underlying causes of poverty and vulnerability, and building sustainable systems, institutions, and capacities for long-term improvement in quality of life. It seeks to build durable solutions over time. If the nexus is not clearly inferable from the narrative for either category, this field should be an empty list []. If only one aspect is clear, only that tag should be used."""
    )
    
    llm_funding_org: List[str] = dspy.OutputField(
        desc="""To list the names of organizations explicitly mentioned in the narrative as providing financial resources (donors) for the project. Names of organizations as they appear in the narrative (e.g., "US Department of Labor", "DFID", "UNICEF"). If no funding organizations are clearly mentioned in the narrative, this field should be an empty list []."""
    )
    
    llm_implementing_org: List[str] = dspy.OutputField(
        desc="""To list the names of organizations explicitly mentioned in the narrative as being responsible for carrying out the project activities (implementing partners). Names of organizations as they appear in the narrative (e.g., "ILO", "Mercy Corps", "Ministry of Education"). If no implementing organizations are clearly mentioned in the narrative, this field should be an empty list []."""
    )

def smart_sample(activities: List[dict], n: int = 100) -> List[dict]:
    """Sample diverse activities including those without descriptions."""
    with_desc = [a for a in activities if a.get('description_narrative')]
    without_desc = [a for a in activities if not a.get('description_narrative') and a.get('title_narrative')]
    
    # 20% without descriptions, 80% with descriptions
    no_desc_count = min(int(n * 0.2), len(without_desc))
    with_desc_count = n - no_desc_count
    
    sample = []
    if no_desc_count > 0:
        sample.extend(random.sample(without_desc, no_desc_count))
    if with_desc_count > 0:
        sample.extend(random.sample(with_desc, min(with_desc_count, len(with_desc))))
    
    return sample

def build_sector_string():
    sector_data = read_json(SECTOR_JSON_PATH)
    sector_text = ""
    for sector in sector_data.get('data')

def generate_labels(activities: List[dict], model: str) -> List[dict]:
    """Generate initial labels using strong model."""
    lm = dspy.LM(model)
    classifier = dspy.ChainOfThought(IATIClassifier)
    
    labeled = []
    with dspy.context(lm=lm):
        for activity in activities:
            try:
                result = classifier(
                    title_narrative=activity.get('title_narrative', ''),
                    description_narrative=activity.get('description_narrative', ''),
                    sector_narrative=activity.get('sector_narrative', '')
                )
                
                activity_copy = activity.copy()
                activity_copy.update({
                    'llm_ref_group': result.llm_ref_group,
                    'llm_target_population': result.llm_target_population,
                    'llm_ref_setting': result.llm_ref_setting,
                    'llm_geographic_focus': result.llm_geographic_focus,
                    'llm_nexus': result.llm_nexus,
                    'llm_funding_org': result.llm_funding_org,
                    'llm_implementing_org': result.llm_implementing_org
                })
                labeled.append(activity_copy)
                break
            except Exception as e:
                print(f"Error: {e}")
                continue
    
    return labeled

def simple_metric(example, prediction, trace=None) -> float:
    """Simple overall accuracy metric."""
    total_score = 0
    total_fields = 0
    
    fields = ['llm_ref_group', 'llm_target_population', 'llm_ref_setting', 
              'llm_geographic_focus', 'llm_nexus', 
              'llm_funding_org', 'llm_implementing_org']
    
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

def prepare_examples(activities: List[dict]) -> List[dspy.Example]:
    """Convert activities to DSPy examples."""
    examples = []
    for activity in activities:
        if not activity.get('title_narrative'):
            continue
            
        example = dspy.Example(
            title_narrative=activity.get('title_narrative', ''),
            description_narrative=activity.get('description_narrative', ''),
            sector_narrative=activity.get('sector_narrative', ''),
            llm_ref_group=activity.get('llm_ref_group', []),
            llm_target_population=activity.get('llm_target_population', []),
            llm_ref_setting=activity.get('llm_ref_setting', []),
            llm_geographic_focus=activity.get('llm_geographic_focus', []),
            llm_nexus=activity.get('llm_nexus', []),
            llm_funding_org=activity.get('llm_funding_org', []),
            llm_implementing_org=activity.get('llm_implementing_org', [])
        ).with_inputs("title_narrative", "description_narrative", "sector_narrative")
        
        examples.append(example)
    
    return examples

def train_model(examples: List[dspy.Example]) -> dspy.Module:
    """Train optimized classifier."""
    # Split data
    split_idx = int(len(examples) * 0.8)
    trainset = examples[:split_idx]
    devset = examples[split_idx:]
    
    # Create classifier
    classifier = dspy.ChainOfThought(IATIClassifier)
    
    # Optimize
    optimizer = dspy.MIPROv2(metric=simple_metric, auto="light")
    optimized = optimizer.compile(
        classifier,
        trainset=trainset,
        max_bootstrapped_demos=3,
        max_labeled_demos=5,
        requires_permission_to_run=False
    )
    
    # Evaluate
    evaluator = dspy.Evaluate(devset=devset, metric=simple_metric)
    score = evaluator(optimized)
    print(f"Final score: {score:.3f}")
    
    return optimized
