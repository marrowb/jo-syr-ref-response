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
        - Activity is conducted by UNHCR or UNOCHA and no detailed description is given

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
        desc="""CRITICAL: Identify populations that are EXPLICITLY and DIRECTLY TARGETED as BENEFICIARIES of the aid program's activities and services. The program must be designed TO SERVE or PROVIDE DIRECT ASSISTANCE TO these populations.

        IMPORTANT DISTINCTION: Do NOT include a population if they are only mentioned as a contextual factor, a reason for the project, or an indirect/potential beneficiary. Focus on who the project's services are DELIVERED TO.

        "refugees": ONLY when the project explicitly states it TARGETS, SERVES, PROVIDES ASSISTANCE TO, or directly BENEFITS refugees as primary beneficiaries.
        - Examples: "assistance to Syrian refugees", "education services for refugee children", "livelihood support for refugee families".
        - If a project aims to "improve infrastructure in areas with high refugee populations," this alone does NOT mean "refugees" are the target population unless the infrastructure is specifically FOR refugees or refugees receive distinct access/services. The target might be "host_communities" or "general_population" of that area.

        DO NOT use "refugees" if:
        - Refugees are mentioned as a cause of a problem the project addresses for a broader community. Example: A project description states, "The influx of refugees has strained local water resources. This project will upgrade the municipal water system." Here, the direct beneficiaries are the users of the municipal water system (likely "general_population" or "host_communities"), NOT "refugees," unless refugees are explicitly stated to receive distinct water services from this project.
        - The project is about general capacity building (e.g., for a government ministry) that might indirectly benefit refugees among others, but does not provide direct services TO refugees.

        "host_communities": ONLY when the project explicitly targets or provides distinct services to local/host populations specifically because they are affected by or are hosting refugees.
        - Examples: "support for vulnerable Jordanians in refugee-hosting areas", "services for host community members to mitigate impact of refugee presence".
        - If a project benefits an entire area that happens to host refugees (e.g., improving a public school for all children in a district), use "general_population" for that district, and add "host_communities" ONLY if host community children/families receive *additional or specific* support beyond the general improvements.

        "general_population": ONLY when the project targets the broader population of an area (national, regional, or local) without a distinct, primary focus on refugees or host communities as separate beneficiary groups receiving differentiated services.
        - Examples: "national health campaign for all Jordanians", "improving public infrastructure for all residents of Amman".
        - If a project targets "all residents of Mafraq Governorate," and Mafraq hosts refugees, the target is still "general_population" of Mafraq, unless refugees or host communities within Mafraq are explicitly singled out for different or additional services.

        Multiple values are allowed ONLY if the program explicitly states it targets multiple groups with distinct or comprehensive services for each.
        If targeting is unclear, ambiguous, or if a group is only mentioned contextually (as a driver of the problem rather than a direct recipient of the solution), DO NOT include them. Be very conservative. Focus on WHO RECEIVES the project's outputs/services directly.
        """
    )

    llm_ref_setting: List[Literal["camp", "urban", "rural"]] = dspy.OutputField(
        desc="""CRITICAL: Identify the SPECIFIC physical setting(s) where project activities are EXPLICITLY STATED to take place. Vague references or broad administrative areas (like a governorate) are NOT sufficient unless they are the most specific detail provided and inherently imply a setting (e.g., "agricultural activities in X governorate" implies rural).

        "camp": ONLY when activities explicitly occur IN or are delivered directly TO RECIPIENTS IN refugee camps.
        - Look for: Named camps ("Za'atari camp", "Azraq camp", "EJC / Emirati Jordanian Camp"), or phrases like "in refugee camps", "camp-based activities", "services within the camps".
        - If a location like "Azraq" is mentioned, and the activity clearly targets refugees or involves camp-like services, "camp" is appropriate. If "Azraq" refers to the town for general population activities, it would be "urban".

        "urban": ONLY when activities explicitly occur in cities, towns, or clearly municipal settings.
        - Look for: Named cities/towns ("Amman", "Irbid city", "Zarqa town"), or phrases like "urban areas", "city centers", "municipal services".
        - Distinguish from broader governorates. "Mafraq Governorate" is not "urban" unless activities are specified in "Mafraq city".

        "rural": ONLY when activities explicitly occur in rural, countryside, agricultural, or non-urban village areas.
        - Look for: Phrases like "rural areas/communities", "villages", "agricultural lands", "pastoral areas", "desert communities" (if distinct from urban centers).
        - Example: "Support to farming communities in Balqa Governorate" would imply "rural".

        Multiple values are allowed ONLY if activities explicitly and clearly span multiple distinct settings (e.g., "services in Azraq camp and Irbid city").

        DO NOT infer setting from:
        - Governorate names *alone* if the activity type doesn't inherently imply a setting (e.g., "meetings in Mafraq Governorate" is not specific enough).
        - Organization types (e.g., UNHCR's presence doesn't automatically mean "camp").
        - General geographic references like "northern Jordan" if no more specific setting is provided.

        If the setting is not explicitly stated, is too broad (e.g., just "Jordan" with no further detail for a non-national project), or if a project has a "national" geographic focus without specifying types of settings (e.g. "urban clinics nationwide"), use an empty list []. Be conservative.
        If a project is described as "nationwide training workshops," and no specific settings like "urban centers" or "rural schools" are mentioned, the setting list should be empty.
        """
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
