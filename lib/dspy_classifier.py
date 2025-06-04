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
        desc="""CRITICAL: Identify refugee nationalities ONLY when refugees are explicitly mentioned as BENEFICIARIES or TARGET POPULATION.

        Use specific nationalities ("Syria", "Palestine", "Iraq", "Yemen", "Sudan") ONLY when:
        - Text explicitly mentions "Syrian refugees", "Palestinian refugees", etc. as beneficiaries
        - Activities are designed specifically for these refugee populations

        Use "Other" ONLY when:
        - Text explicitly mentions refugees from other countries as beneficiaries (e.g., "Somali refugees")

        Use "mixed_or_unspecified_refugees" ONLY when:
        - Text mentions "refugees" as beneficiaries but nationality not specified
        - UNHCR/UNRWA projects with refugee focus but no nationality breakdown

        EXAMPLES:
        - "Protection from Sexual Exploitation targeting Syrian refugees and host communities" → ["Syria"]
        - "UNICEF child abuse reporting system at UNRWA centres" → ["Palestine"] (UNRWA serves Palestinians)
        - "Energy toolkit responsive to women and girls needs in refugee settings" → ["mixed_or_unspecified_refugees"]
        - "Administrative costs and operating expenses" → [] (no refugees targeted)

        Empty list [] if refugees not explicitly targeted as beneficiaries."""
    )

    llm_target_population: List[
        Literal["refugees", "host_communities", "general_population"]
    ] = dspy.OutputField(
        desc="""CRITICAL: Identify populations that DIRECTLY RECEIVE project services. Be extremely conservative.

        "refugees": ONLY when text explicitly states refugees receive direct services
        - REQUIRED phrases: "assistance to refugees", "services for refugees", "refugee beneficiaries", "targeting refugees"
        - UNRWA projects automatically include refugees (they serve Palestinians)
        - UNHCR projects typically serve refugees

        "host_communities": ONLY when text explicitly mentions serving local/host populations distinctly
        - REQUIRED phrases: "host community support", "vulnerable Jordanians", "host populations"

        "general_population": ONLY for projects serving broader population without refugee distinction
        - National programs, public infrastructure, general services

        AUTOMATIC EMPTY LIST [] for:
        - Administrative projects ("Administration", "Operations", "Miscellaneous", "Travel", "Oversight")
        - Unclear or vague descriptions
        - Projects mentioning refugees only as context, not beneficiaries

        EXAMPLES:
        - "Protection targeting Syrian refugees and host communities" → ["refugees", "host_communities"]
        - "UNICEF child abuse reporting at UNRWA centres" → ["refugees"] (UNRWA serves refugees)
        - "Administrative costs and operating expenses" → []
        - "Red Cross activities in Jordan" (no beneficiary details) → []
        - "Energy toolkit for women and girls in refugee settings" → ["refugees"]"""
    )

    llm_ref_setting: List[Literal["camp", "urban", "rural"]] = dspy.OutputField(
        desc="""Identify ALL physical settings where activities occur. MULTIPLE values required for multi-location projects.

        "camp": Any mention of refugee camps, named camps (Za'atari, Azraq, EJC, etc.), "camp settings"
        "urban": Cities, towns, urban areas, municipal services
        "rural": Villages, rural communities, agricultural areas

        CRITICAL - INCLUDE MULTIPLE SETTINGS when:
        - "throughout Jordan", "across the country", "six governorates" → likely ["urban", "rural", "camp"]
        - "all across the country through six governorates" → ["urban", "rural", "camp"]
        - Multiple governorates mentioned → likely ["urban", "rural"]
        - National scope projects → typically ["urban", "rural"]

        EXAMPLES:
        - "targeting six governorates of Irbid, Madaba, Amman, Karak, Ma'an and Tafileh" → ["urban", "rural", "camp"]
        - "Primary Health Care in Jordan" → ["urban", "rural"]
        - "activities at UNRWA centres and NGOs" → ["camp", "urban"]
        - "Amman" only → ["urban"]

        Empty list [] only if NO geographic details provided."""
    )

    llm_geographic_focus: List[str] = dspy.OutputField(
        desc="""List specific locations mentioned, using EXACT names from text.

        Include:
        - Governorates: "Irbid", "Madaba", "Amman", "Karak", "Ma'an", "Tafileh", "Al Karak", "Al Tafilah"
        - Cities: "Amman", "Washington DC", "Stockholm", etc.
        - Regions: "Middle East and North Africa", "northern Jordan"
        - Countries: "Jordan", "Ukraine", etc.
        - Use "national" if explicitly described as nationwide scope

        EXTRACT ALL mentioned locations, not just primary focus.

        EXAMPLES:
        - "six governorates of Irbid, Madaba, Amman, Karak, Ma'an and Tafileh" → ["Irbid", "Madaba", "Amman", "Karak", "Ma'an", "Tafileh"]
        - "Washington DC, USA/Amman, Jordan" → ["Washington DC", "Amman", "Jordan"]
        - "throughout Jordan" → ["national"]"""
    )

    llm_nexus: List[Literal["humanitarian", "development"]] = dspy.OutputField(
        desc="""Categorize project approach. REFUGEE PROJECTS typically require BOTH categories.

        "humanitarian": Emergency response, protection, immediate assistance, crisis response, PSEA, emergency health
        "development": Capacity building, infrastructure, institutional strengthening, long-term solutions, education systems

        CRITICAL - Use BOTH ["humanitarian", "development"] when:
        - Refugee protection + capacity building
        - UNRWA projects (always both)
        - UNICEF refugee work (typically both)
        - Projects combining immediate assistance with institutional strengthening
        - Child protection + system development

        EXAMPLES:
        - "Protection from Sexual Exploitation + strengthening social protection systems" → ["humanitarian", "development"]
        - "UNICEF child abuse reporting system" → ["humanitarian", "development"]
        - "Administrative costs only" → []
        - "Water infrastructure program" → ["development"]
        - "Emergency energy toolkit" → ["humanitarian"]

        Single category only if CLEARLY just one type. Empty list [] if unclear."""
    )

    llm_funding_org: List[str] = dspy.OutputField(
        desc="""List ALL organizations providing funding, using EXACT names from text.

        Search in ALL narrative fields for funding sources. Include ALL name variations:
        - Full names AND abbreviations if both mentioned
        - Different language versions if provided
        - Government departments and agencies

        EXAMPLES:
        - "Jordan Humanitarian Fund", "United Nations Office for the Coordination of Humanitarian Affairs" → ["Jordan Humanitarian Fund", "United Nations Office for the Coordination of Humanitarian Affairs"]
        - "Sweden" + "Swedish International Development Cooperation Agency" → ["Sweden", "Swedish International Development Cooperation Agency"]
        - "U.S. Agency for International Development" + "Department of State" → ["U.S. Agency for International Development", "Department of State"]
        - "BMZ" + "Federal Ministry for Economic Cooperation and Development" → ["Bundesministerium für wirtschaftliche Zusammenarbeit und Entwicklung (BMZ)", "Federal Ministry for Economic Cooperation and Development (BMZ)"]

        Look especially in: transaction_provider_org_narrative, participating_org_narrative, description text.
        Empty list [] only if NO funding sources mentioned."""
    )

    llm_implementing_org: List[str] = dspy.OutputField(
        desc="""List ALL organizations carrying out activities, using EXACT names from text.

        Include ALL implementing partners mentioned:
        - Primary implementers and sub-contractors
        - Government ministries/agencies if implementing
        - NGOs, UN agencies, private companies
        - Multiple partners if mentioned

        EXAMPLES:
        - "INTERSOS" + "UNRWA" + "NGOs" → ["INTERSOS", "UNRWA", "NGOs"]
        - "U.S. Agency for International Development" + "Invitational Travelers - USAID" → ["U.S. Agency for International Development", "Invitational Travelers - USAID"]
        - "International Labour Organization (ILO)" + "Development and Employment Fund" → ["International Labour Organization (ILO)", "Development and Employment Fund", "Vocational Training Corporation (VTC)"]

        Look especially in: transaction_receiver_org_narrative, participating_org_narrative, description text for "implemented by", "carried out by", partner organizations.
        
        Include the reporting organization if they're also implementing (not just reporting)."""
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
