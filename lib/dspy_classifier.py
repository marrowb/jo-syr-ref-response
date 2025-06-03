import random
from typing import List, Literal

import dspy

from definitions import DSPY_CONFIG, GEMINI_API_KEY


class IATIClassifier(dspy.Signature):
    """Classify IATI aid activities based on narrative elements using IATI sector codes and refugee/humanitarian context."""

    title_narrative: str = dspy.InputField(desc="Project title")
    description_narrative: str = dspy.InputField(
        desc="Project description (may be empty)"
    )
    sector_narrative: str = dspy.InputField(desc="Sector-related narrative text")

    reporting_org_narrative: str = dspy.InputField(
        desc="Name of the organisation issuing the report"
    )
    participating_org_narrative: str = dspy.InputField(
        desc="Name of an organisation involved with the activity (donor, fund, agency, etc.)"
    )
    other_identifier_owner_org_narrative: str = dspy.InputField(
        desc="Name of the organisation that owns the other identifier being reported"
    )
    activity_date_narrative: str = dspy.InputField(
        desc="Textual description of activity dates (e.g. 2011Q1) for less specific dates"
    )
    location_name_narrative: str = dspy.InputField(
        desc="Human-readable name for the location"
    )
    location_description_narrative: str = dspy.InputField(
        desc="Description that qualifies the location, not the activity"
    )
    location_activity_description_narrative: str = dspy.InputField(
        desc="Description that qualifies the activity taking place at the location"
    )
    tag_narrative: str = dspy.InputField(
        desc="Description of categorisations from established taxonomies"
    )
    country_budget_items_budget_item_description_narrative: str = dspy.InputField(
        desc="Human-readable description of the budget-item"
    )
    humanitarian_scope_narrative: str = dspy.InputField(
        desc="Description of the humanitarian scope code specified"
    )
    policy_marker_narrative: str = dspy.InputField(
        desc="Description of the policy marker (only for reporting organisation's own vocabulary)"
    )
    planned_disbursement_provider_org_narrative: str = dspy.InputField(
        desc="Name of the organisation from which the planned disbursement will originate"
    )
    planned_disbursement_receiver_org_narrative: str = dspy.InputField(
        desc="Name of the organisation receiving the money from the planned disbursement"
    )
    transaction_description_narrative: str = dspy.InputField(
        desc="Human-readable description of the transaction"
    )
    transaction_provider_org_narrative: str = dspy.InputField(
        desc="Name of the organisation from which the transaction originated"
    )
    transaction_receiver_org_narrative: str = dspy.InputField(
        desc="Name of the organisation receiving the money from the transaction"
    )
    document_link_title_narrative: str = dspy.InputField(
        desc="Title of the document being linked"
    )
    document_link_description_narrative: str = dspy.InputField(
        desc="Description of the document being linked"
    )
    conditions_condition_narrative: str = dspy.InputField(
        desc="Text of a specific condition attached to the activity"
    )
    result_title_narrative: str = dspy.InputField(
        desc="Title of the result being reported"
    )
    result_description_narrative: str = dspy.InputField(
        desc="Description of the result being reported"
    )
    result_document_link_title_narrative: str = dspy.InputField(
        desc="Title of document linked to the result"
    )
    result_document_link_description_narrative: str = dspy.InputField(
        desc="Description of document linked to the result"
    )
    result_indicator_title_narrative: str = dspy.InputField(
        desc="Title of the indicator that meets the results"
    )
    result_indicator_description_narrative: str = dspy.InputField(
        desc="Description of the indicator that meets the results"
    )
    result_indicator_document_link_title_narrative: str = dspy.InputField(
        desc="Title of document linked to the result indicator"
    )
    result_indicator_document_link_description_narrative: str = dspy.InputField(
        desc="Description of document linked to the result indicator"
    )
    result_indicator_baseline_document_link_title_narrative: str = dspy.InputField(
        desc="Title of document linked to the baseline value"
    )
    result_indicator_baseline_document_link_description_narrative: str = (
        dspy.InputField(desc="Description of document linked to the baseline value")
    )
    result_indicator_baseline_comment_narrative: str = dspy.InputField(
        desc="Comment narrative for the baseline value of the indicator"
    )
    result_indicator_period_target_comment_narrative: str = dspy.InputField(
        desc="Comment narrative for the target milestone for this period"
    )
    result_indicator_period_target_document_link_title_narrative: str = dspy.InputField(
        desc="Title of document linked to the period target"
    )
    result_indicator_period_target_document_link_description_narrative: str = (
        dspy.InputField(desc="Description of document linked to the period target")
    )
    result_indicator_period_actual_comment_narrative: str = dspy.InputField(
        desc="Comment narrative for the actual result achieved for this period"
    )
    result_indicator_period_actual_document_link_title_narrative: str = dspy.InputField(
        desc="Title of document linked to the actual period result"
    )
    result_indicator_period_actual_document_link_description_narrative: str = (
        dspy.InputField(
            desc="Description of document linked to the actual period result"
        )
    )

    llm_ref_group: List[
        Literal[
            "Syria",
            "Palestine",
            "Iraq",
            "Yemen",
            "Sudan",
            "Other",
            "mixed_or_unspecified_refugees",
        ]
    ] = dspy.OutputField(
        desc="""CRITICAL: Identify refugee nationalities ONLY when refugees are explicitly mentioned as BENEFICIARIES or TARGET POPULATION of the aid program.

        Use specific nationalities ("Syria", "Palestine", "Iraq", "Yemen", "Sudan") ONLY when:
        - Program explicitly targets/serves refugees from these countries
        - "Syrian refugees", "Palestinian refugees", etc. are mentioned as beneficiaries
        - Activities are designed specifically for these refugee populations

        Use "Other" ONLY when:
        - Program explicitly targets refugees from countries not listed (e.g., "Somali refugees", "Sudanese refugees")
        - Must be clear they are beneficiaries, not just mentioned

        Use "mixed_or_unspecified_refugees" ONLY when:
        - Program explicitly targets "refugees" as beneficiaries but nationality is not specified
        - Multiple refugee groups are targeted but not individually identifiable
        - "refugee populations", "refugee beneficiaries" without nationality breakdown

        DO NOT use any values if:
        - Refugees are only mentioned in context/background
        - Program is about refugee coordination/management without direct service
        - Activities happen in refugee areas but don't target refugees as beneficiaries
        - General capacity building that may indirectly affect refugees

        Empty list [] if no refugees are explicitly targeted as beneficiaries. Be very conservative - targeting must be explicit and clear."""
    )

    llm_target_population: List[
        Literal["refugees", "host_communities", "general_population"]
    ] = dspy.OutputField(
        desc="""CRITICAL: Identify populations that are EXPLICITLY TARGETED as beneficiaries of the aid program. Mere mention is NOT sufficient - the program must be designed to serve these populations.

        "refugees": ONLY when the project explicitly states it TARGETS, SERVES, or BENEFITS refugees as primary beneficiaries. Look for:
        - "targeting refugees", "serving refugee populations", "benefiting refugees"
        - "refugee beneficiaries", "assistance to refugees", "support for refugees"
        - Programs specifically designed for refugee needs (livelihood, protection, education for refugees)
        - Services delivered TO refugees (not just in refugee areas)
        
        DO NOT use "refugees" if:
        - Refugees are only mentioned in context or background
        - Program is about refugee management/coordination without direct service
        - Activities happen in refugee areas but don't target refugees specifically
        - General capacity building that may indirectly affect refugees

        "host_communities": ONLY when explicitly targeting local/host populations affected by refugee presence:
        - "vulnerable Jordanians", "host community members", "local communities hosting refugees"
        - "communities affected by refugee influx", "vulnerable locals in refugee-hosting areas"
        - Programs specifically for host community needs/tensions

        "general_population": ONLY when targeting broader national population without refugee-specific focus:
        - "all Jordanians", "national program", "general public", "citizens"
        - Government capacity building, national systems strengthening
        - Programs with no refugee/displacement context

        Multiple values allowed ONLY if program explicitly targets multiple groups. If targeting is unclear or ambiguous, use empty list []. Be conservative - when in doubt, leave empty."""
    )

    llm_ref_setting: List[Literal["camp", "urban", "rural"]] = dspy.OutputField(
        desc="""CRITICAL: Identify the SPECIFIC physical setting where project activities are EXPLICITLY stated to occur. Vague references are not sufficient.

        "camp": ONLY when activities explicitly occur in refugee camps:
        - Named camps: "Za'atari camp", "Azraq camp", "EJC", "Emirati Jordanian Camp"
        - Clear camp references: "in refugee camps", "camp-based activities", "within the camps"
        - Camp-specific services: "camp management", "camp facilities", "camp infrastructure"

        "urban": ONLY when activities explicitly occur in cities/towns:
        - Named cities: "Amman", "Irbid", "Zarqa", "Mafraq city", "Aqaba"
        - Clear urban references: "urban areas", "city centers", "metropolitan areas", "municipal"
        - Urban-specific context: "city-based services", "urban planning", "downtown"

        "rural": ONLY when activities explicitly occur in rural/countryside areas:
        - Clear rural references: "rural areas", "countryside", "villages", "remote areas"
        - Agricultural context: "farming communities", "agricultural areas", "pastoral regions"
        - Non-urban geographic: "border villages", "desert communities", "mountainous areas"

        Multiple values allowed ONLY if activities explicitly span multiple settings (e.g., "activities in both camps and urban areas").

        DO NOT infer setting from:
        - Governorate names alone (e.g., "Mafraq governorate" without specifics)
        - Organization types (UNHCR doesn't automatically mean camps)
        - General geographic references ("northern Jordan" without specifics)

        If setting is not explicitly clear, use empty list []. Be conservative."""
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


def smart_sample(activities: List[dict], n: int = 150) -> List[dict]:
    """Sample diverse activities including those without descriptions."""
    with_desc = [a for a in activities if a.get("description_narrative")]
    without_desc = [
        a
        for a in activities
        if not a.get("description_narrative") and a.get("title_narrative")
    ]

    # 10% without descriptions, 90% with descriptions
    no_desc_count = min(int(n * 0.1), len(without_desc))
    with_desc_count = n - no_desc_count

    sample = []
    if no_desc_count > 0:
        sample.extend(random.sample(without_desc, no_desc_count))
    if with_desc_count > 0:
        sample.extend(random.sample(with_desc, min(with_desc_count, len(with_desc))))

    return sample


def generate_labels(activities: List[dict], model: str) -> List[dict]:
    """Generate initial labels using strong model."""
    lm = dspy.LM(model)
    classifier = dspy.ChainOfThought(IATIClassifier)

    labeled = []
    with dspy.context(lm=lm):
        for i, activity in enumerate(activities):
            try:
                result = classifier(
                    reporting_org_narrative=activity.get("reporting_org_narrative", ""),
                    title_narrative=activity.get("title_narrative", ""),
                    description_narrative=activity.get("description_narrative", ""),
                    participating_org_narrative=activity.get(
                        "participating_org_narrative", ""
                    ),
                    other_identifier_owner_org_narrative=activity.get(
                        "other_identifier_owner_org_narrative", ""
                    ),
                    activity_date_narrative=activity.get("activity_date_narrative", ""),
                    location_name_narrative=activity.get("location_name_narrative", ""),
                    location_description_narrative=activity.get(
                        "location_description_narrative", ""
                    ),
                    location_activity_description_narrative=activity.get(
                        "location_activity_description_narrative", ""
                    ),
                    sector_narrative=activity.get("sector_narrative", ""),
                    tag_narrative=activity.get("tag_narrative", ""),
                    country_budget_items_budget_item_description_narrative=activity.get(
                        "country_budget_items_budget_item_description_narrative", ""
                    ),
                    humanitarian_scope_narrative=activity.get(
                        "humanitarian_scope_narrative", ""
                    ),
                    policy_marker_narrative=activity.get("policy_marker_narrative", ""),
                    planned_disbursement_provider_org_narrative=activity.get(
                        "planned_disbursement_provider_org_narrative", ""
                    ),
                    planned_disbursement_receiver_org_narrative=activity.get(
                        "planned_disbursement_receiver_org_narrative", ""
                    ),
                    transaction_description_narrative=activity.get(
                        "transaction_description_narrative", ""
                    ),
                    transaction_provider_org_narrative=activity.get(
                        "transaction_provider_org_narrative", ""
                    ),
                    transaction_receiver_org_narrative=activity.get(
                        "transaction_receiver_org_narrative", ""
                    ),
                    document_link_title_narrative=activity.get(
                        "document_link_title_narrative", ""
                    ),
                    document_link_description_narrative=activity.get(
                        "document_link_description_narrative", ""
                    ),
                    conditions_condition_narrative=activity.get(
                        "conditions_condition_narrative", ""
                    ),
                    result_title_narrative=activity.get("result_title_narrative", ""),
                    result_description_narrative=activity.get(
                        "result_description_narrative", ""
                    ),
                    result_document_link_title_narrative=activity.get(
                        "result_document_link_title_narrative", ""
                    ),
                    result_document_link_description_narrative=activity.get(
                        "result_document_link_description_narrative", ""
                    ),
                    result_indicator_title_narrative=activity.get(
                        "result_indicator_title_narrative", ""
                    ),
                    result_indicator_description_narrative=activity.get(
                        "result_indicator_description_narrative", ""
                    ),
                    result_indicator_document_link_title_narrative=activity.get(
                        "result_indicator_document_link_title_narrative", ""
                    ),
                    result_indicator_document_link_description_narrative=activity.get(
                        "result_indicator_document_link_description_narrative", ""
                    ),
                    result_indicator_baseline_document_link_title_narrative=activity.get(
                        "result_indicator_baseline_document_link_title_narrative", ""
                    ),
                    result_indicator_baseline_document_link_description_narrative=activity.get(
                        "result_indicator_baseline_document_link_description_narrative",
                        "",
                    ),
                    result_indicator_baseline_comment_narrative=activity.get(
                        "result_indicator_baseline_comment_narrative", ""
                    ),
                    result_indicator_period_target_comment_narrative=activity.get(
                        "result_indicator_period_target_comment_narrative", ""
                    ),
                    result_indicator_period_target_document_link_title_narrative=activity.get(
                        "result_indicator_period_target_document_link_title_narrative",
                        "",
                    ),
                    result_indicator_period_target_document_link_description_narrative=activity.get(
                        "result_indicator_period_target_document_link_description_narrative",
                        "",
                    ),
                    result_indicator_period_actual_comment_narrative=activity.get(
                        "result_indicator_period_actual_comment_narrative", ""
                    ),
                    result_indicator_period_actual_document_link_title_narrative=activity.get(
                        "result_indicator_period_actual_document_link_title_narrative",
                        "",
                    ),
                    result_indicator_period_actual_document_link_description_narrative=activity.get(
                        "result_indicator_period_actual_document_link_description_narrative",
                        "",
                    ),
                    iati_identifier=activity.get("iati_identifier", ""),
                    iati_identifier_exact=activity.get("iati_identifier_exact", ""),
                )

                activity_copy = activity.copy()
                result_dict = result.toDict()
                activity_copy.update(
                    {
                        "llm_ref_group": result_dict.get("llm_ref_group"),
                        "llm_target_population": result_dict.get(
                            "llm_target_population"
                        ),
                        "llm_ref_setting": result_dict.get("llm_ref_setting"),
                        "llm_geographic_focus": result_dict.get("llm_geographic_focus"),
                        "llm_nexus": result_dict.get("llm_nexus"),
                        "llm_funding_org": result_dict.get("llm_funding_org"),
                        "llm_implementing_org": result_dict.get("llm_implementing_org"),
                        # Initialize tracking fields
                        "human_edited": 0,
                        "notes": "",
                        "unclear": 0,
                    }
                )
                labeled.append(activity_copy)
                print(
                    f"Classified activity number {i}...:\nTitle:\n{activity.get('title_narrative')} \n Description:\n{activity.get('description_narrative')} \n Classification: \n{result_dict}"
                )
            except Exception as e:
                print(f"Error: {e}")
                continue
    print("Classified all results.")
    return labeled


