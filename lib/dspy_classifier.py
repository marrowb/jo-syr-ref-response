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
        desc="""CRITICAL: Identify populations that DIRECTLY RECEIVE project services. Be EXTREMELY conservative.

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
        - "Expert exchange", "professional exchanges" (no clear beneficiaries)
        - "Scholarship distribution" without beneficiary details
        - Projects about "mapping", "assessment", "evaluation"
        - Budget/expenditure projects without service details
        - Any project where you have to guess who benefits

        EXAMPLES:
        - "Protection targeting Syrian refugees and host communities" → ["refugees", "host_communities"]
        - "UNICEF child abuse reporting at UNRWA centres" → ["refugees"] (UNRWA serves refugees)
        - "Administrative costs and operating expenses" → []
        - "DISTRIBUTION OF SCHOLARSHIPS" without beneficiary details → []
        - "Project support for professional exchanges" → []
        - "Mapping of gender equality" → []
        - "Healthy Ecosystems for Rangeland Development" without beneficiary details → []"""
    )

    llm_ref_setting: List[Literal["camp", "urban", "rural"]] = dspy.OutputField(
        desc="""Identify physical settings ONLY when explicitly mentioned. Be VERY CONSERVATIVE.

        "camp": Any mention of refugee camps, named camps (Za'atari, Azraq, EJC, etc.), "camp settings", "Marka Camp"
        "urban": Cities, towns, urban areas, municipal services explicitly mentioned
        "rural": Villages, rural communities, agricultural areas explicitly mentioned

        INCLUDE MULTIPLE SETTINGS when:
        - "throughout Jordan" with activity details → likely ["urban", "rural", "camp"]
        - "all across the country through six governorates" → ["urban", "rural", "camp"]
        - Multiple governorates mentioned with service delivery → likely ["urban", "rural"]

        EMPTY LIST [] for:
        - Administrative/budget/expenditure projects
        - Projects with no geographic details beyond country name
        - "National" programs without setting specification
        - Projects where setting cannot be determined

        EXAMPLES:
        - "targeting six governorates with protection services" → ["urban", "rural", "camp"]
        - "Primary Health Care in Jordan" → ["urban", "rural"]
        - "activities at UNRWA centres and NGOs" → ["camp", "urban"]
        - "2020Programme Budget - Health Programme" → [] (no settings mentioned)
        - "Jordan School Construction throughout Jordan" → ["urban", "rural"] (schools typically not in camps)"""
    )

    llm_geographic_focus: List[str] = dspy.OutputField(
        desc="""List specific locations mentioned, using EXACT names from text. Handle name variations carefully.

        CRITICAL RULES:
        - Use EXACT names as they appear: "Karak" and "Al Karak" are DIFFERENT if both mentioned
        - Do NOT add "Jordan" if only sub-national locations mentioned (e.g., just "Amman" = ["Amman"], not ["Amman", "Jordan"])
        - Use "national" ONLY if explicitly stated as nationwide/country-wide scope
        - For target locations only - ignore source countries in exchange programs
        - Extract locations from titles AND descriptions

        EXAMPLES:
        - "six governorates of Irbid, Madaba, Amman, Karak, Ma'an and Tafileh" → ["Irbid", "Madaba", "Amman", "Karak", "Ma'an", "Tafileh"] (use names as written)
        - "seminar with participants from Egypt, Jordan and Tunisia" → ["Egypt", "Jordan", "Tunisia"] (all mentioned)
        - "capacity building support to Jordan audit institution" → ["Jordan"] (national scope)
        - "Water Resources Management in Amman" → ["Amman"] (not ["Amman", "Jordan"])
        - "MENA region including Syria, Jordan, Lebanon" → ["Syria", "Jordan", "Lebanon", "Middle East and North Africa"]"""
    )

    llm_nexus: List[Literal["humanitarian", "development"]] = dspy.OutputField(
        desc="""Categorize project approach. REFUGEE PROJECTS typically require BOTH categories.

        "humanitarian": Emergency response, protection, immediate assistance, crisis response, PSEA, emergency health, COVID emergency response
        "development": Capacity building, infrastructure, institutional strengthening, long-term solutions, education systems

        SPECIAL CASES:
        - Administrative work with "GLIDE: (COVID-19)" tags → include "humanitarian" (emergency response context)
        - Budget projects without clear beneficiaries or context → []

        CRITICAL - Use BOTH ["humanitarian", "development"] when:
        - Refugee protection + capacity building
        - UNRWA projects (always both)
        - UNICEF refugee work (typically both)
        - Projects combining immediate assistance with institutional strengthening

        EXAMPLES:
        - "Protection from Sexual Exploitation + strengthening social protection systems" → ["humanitarian", "development"]
        - "UNICEF child abuse reporting system" → ["humanitarian", "development"]
        - "Administrative costs" + "GLIDE: (COVID-19)" → ["humanitarian"]
        - "2020Programme Budget" with no COVID context → []
        - "Water infrastructure program" → ["development"]"""
    )

    llm_funding_org: List[str] = dspy.OutputField(
        desc="""List organizations providing funding. Look carefully in description text for funding mentions.

        SEARCH STRATEGIES:
        - Look for: "funded by", "financed by", "provided by", "support from", "Ko-Finanzierung"
        - Check descriptions for co-financing: "Ko-Finanzierung EU", "Neighbourhood Investment Plattform (NIP)"
        - Transaction providers are often funders
        - Reporting org may also be a funder

        CRITICAL RULES:
        - Include abbreviated forms mentioned: if text says "GEF" include both "Global Environment Facility" and "GEF"
        - Look for co-financing: "Ko-Finanzierung EU" means EU is a funder
        - Extract from titles: "JHF-OCHA funded project" → "Jordan Humanitarian Fund"
        - Don't duplicate same organization with slightly different names

        EXAMPLES:
        - "25 Mio. EUR aus Mitteln der Neighbourhood Investment Plattform (NIP) (Ko-Finanzierung EU)" → include "EU"
        - "Jordan Humanitarian Fund" + "United Nations Office for the Coordination of Humanitarian Affairs" → both funders
        - "Development and Employment Fund (DEF) who will be considered the project donor" → include "Development and Employment Fund"
        - "GEF" in transactions → include both "Global Environment Facility" and "GEF" """
    )

    llm_implementing_org: List[str] = dspy.OutputField(
        desc="""List organizations carrying out activities. Look in titles, descriptions, transaction receivers, and participating orgs.

        EXTRACTION RULES:
        - Extract from titles: "ICRC 1999 Jordan" → include "ICRC"
        - Look for: "implemented by", "carried out by", "piloted in", government partners
        - Government ministries mentioned as partners are implementers
        - Transaction receivers are often implementers
        - Organizations mentioned as delivering services

        EXAMPLES:
        - "ICRC 1999 Jordan" title → ["ICRC"]
        - "support the Jordanian Ministry of Education reform program" → ["Jordanian Ministry of Education", "International Relief and Development"]
        - "at UNRWA centres and NGOs" → ["UNRWA", "NGOs"]
        - "DEF will pilot the KAB programme in the VTC" → ["Development and Employment Fund", "Vocational Training Corporation"]
        - "INTERSOS will focus on strengthening CBO social protection systems" → ["INTERSOS"]
        - Include exact names: "unrwa" and "United Nations Relief and Works Agency" both if mentioned"""
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
