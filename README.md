# International Aid Flows in the Syrian Refugee Response in Jordan
This project examines funding for the Syrian refugee response in Jordan since the beginning of the Syrian Civil war. It is split into two components:
1. A comparison of UN funding for the response versus the number of Syrian refugees registered by UNHCR over time.
2. The construction of a funding dataset that includes bilateral aid for Syrian refugees with data from the International Aid Transparency Initiative.


# UNHCR Registered Refugees vs. Donor Contributions to the Syrian Refugee Response in Jordan
## Replication
Cloning this git repo will allow this code to run smoothly. The data will only be as recent as April 30, 2025. If you want to replicate this code with more recent data, instructions for obtaining it are below in data sources.

## Data Sources
### UNHCR Refugee Data
“Situation Syria Regional Refugee Response,” last updated April 30, 2025. [link](https://data.unhcr.org/en/situations/syria/location/36)
* Click the JSON button by "Refugees from Syria by Date" and save the file. That is located at [link]("./data/unhcr.json")

### UN OCHA FTS Data
“Syrian Arab Republic Regional Refugee and Resilience Plan (3RP),” UNOCHA Financial Tracking Service, 2013-2024 [link](https://fts.unocha.org/plans/1168/flows?f%5B0%5D=flowStatus%3Apaid).
* Need to navigate to the funding page for each year from 2013-2024 and click the download button. Those Excel files are located [here]("./data/ocha-fts/")

## Figures
* [Funding vs. Total Individuals](./figures/contributions_vs_individuals.png)
* [Funding per Refugee](./figures/contributions_vs_individuals.png)


# IATI Aid Activity Classification Project

A machine learning pipeline for automatically classifying International Aid Transparency Initiative (IATI) aid activities using DSPy and Google's Gemini models, with a focus on identifying refugee-related funding and programs in Jordan.

## Project Overview

The International Aid Transparency Initiative (IATI) is a global standard for publishing aid, development, and humanitarian data. With thousands of activities published by hundreds of organizations, manually analyzing this data to understand funding flows, beneficiaries, and implementation patterns is extremely challenging.

This project addresses the Syrian refugee crisis context, where Jordan hosts over 650,000 registered Syrian refugees alongside Palestinian refugees and other displaced populations. Understanding which aid activities target specific refugee populations, their geographic distribution, and implementation modalities is crucial for:

- **Coordination**: Avoiding duplication and identifying gaps in assistance
- **Accountability**: Tracking how humanitarian and development funding reaches intended beneficiaries  
- **Analysis**: Understanding the humanitarian-development nexus in protracted displacement
- **Policy**: Informing evidence-based decisions about refugee assistance programs

**Goal**: Automatically classify IATI aid activities to extract structured information about refugee-related funding, target populations, geographic focus, and organizational relationships.

## Key Features

### 🎯 Multi-field Classification
Extracts 7 key dimensions from aid activity narratives:

- **Refugee Nationality Groups**: Syria, Palestine, Iraq, Yemen, Sudan, Other, mixed/unspecified
- **Target Populations**: refugees, host communities, general population  
- **Geographic Settings**: camp, urban, rural environments
- **Geographic Focus**: specific locations and administrative areas mentioned
- **Humanitarian vs Development Nexus**: emergency response vs. long-term capacity building
- **Funding Organizations**: donors and financial contributors
- **Implementing Organizations**: agencies carrying out activities

### 🤖 Advanced ML Pipeline
- **DSPy Framework**: Declarative Self-improving Language Programs for robust few-shot learning
- **Google Gemini Models**: Gemini 2.5 Pro for training, Gemini 2.0 Flash for inference
- **Chain-of-Thought Reasoning**: Structured prompts with detailed classification logic
- **Weighted Metrics**: Performance optimization prioritizing critical fields

### 💰 Currency Conversion
- **Multi-currency Support**: Converts all financial transactions to USD
- **Federal Reserve Data**: Real-time exchange rates for major currencies
- **Pegged Currencies**: Special handling for JOD, SAR, and other fixed rates
- **Historical Accuracy**: Date-specific exchange rate matching

### 👥 Interactive Validation
- **Human-in-the-Loop**: Interactive review and correction of model predictions
- **Field-specific Editing**: Targeted correction of individual classification fields
- **Progress Tracking**: Resume validation sessions and track human edits
- **Quality Assurance**: Built-in validation rules and error detection

### ⚡ Batch Processing
- **Async Processing**: Concurrent classification with rate limiting
- **Progress Persistence**: Resume interrupted classification runs
- **Error Handling**: Robust retry logic and error logging
- **Scalable Architecture**: Process thousands of activities efficiently

## Technical Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   IATI API      │    │   DSPy Pipeline  │    │   MLflow        │
│   Data Source   │───▶│   Classification │───▶│   Tracking      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Federal       │    │   Currency       │    │   Validated     │
│   Reserve XR    │───▶│   Conversion     │───▶│   Results       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

- **Framework**: DSPy (Declarative Self-improving Language Programs)
- **Models**: Google Gemini 2.5 Pro (training) and Gemini 2.0 Flash (inference)  
- **Data Source**: IATI Datastore API with 40+ narrative fields
- **Tracking**: MLflow for experiment management and model versioning
- **Processing**: Pandas for data manipulation, asyncio for concurrent processing
- **Storage**: JSON for structured data, CSV for tabular analysis

## Installation & Setup

```bash
# Clone repository
git clone [repository-url]
cd iati-aid-classification

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Add your API keys to .env:
# IATI_API_KEY=your_iati_key (optional - API is currently open)
# GEMINI_API_KEY=your_gemini_api_key
```

### Requirements
- Python 3.8+
- Google Cloud API access for Gemini models
- ~2GB disk space for data and models
- Internet connection for IATI API and exchange rate data

## Project Structure

```
├── data/
│   ├── iati/                           # IATI activity and transaction data
│   │   ├── jordan_activities.json      # Raw activity data
│   │   ├── batch-classify/             # Classification results by timestamp
│   │   └── model/                      # Training data (labeled/unlabeled)
│   ├── ocha-fts/                       # UN OCHA Financial Tracking Service data
│   └── xr/                             # Federal Reserve exchange rate data
├── iati/
│   ├── dspy_run.py                     # Main DSPy pipeline runner
│   └── iati_build_usd_transactions.py # Transaction processing and USD conversion
├── lib/
│   ├── dspy_batch_classify.py          # Async batch classification
│   ├── dspy_classifier.py              # Core DSPy classifier definition
│   ├── dspy_metrics.py                 # Evaluation metrics and logging
│   ├── dspy_optimizer.py               # Model training and optimization
│   ├── iati_datastore_utils.py         # IATI API client utilities
│   ├── iati_codelist_utils.py          # IATI standard code lists
│   ├── util_labels.py                  # Interactive label validation
│   ├── util_xr.py                      # Exchange rate processing
│   └── util_*.py                       # Other utility functions
├── reference/iati/codelists/           # IATI standard code lists (JSON)
├── models/                             # Trained model artifacts
├── definitions.py                      # Configuration and constants
└── requirements.txt                    # Python dependencies
```
## Pipeline

The data pipeline transforms raw IATI aid data into a structured dataset of refugee-related funding flows. This process addresses a critical challenge: among thousands of aid activities in Jordan, which ones specifically target Syrian refugees versus other populations, and how much funding do they represent?

### 1. Fetching Jordan Activities

We start by retrieving all aid activities where Jordan is involved, either as the primary recipient country or as a transaction destination. This captures both direct bilateral aid to Jordan and regional programs that include Jordan as a beneficiary.

```py
from lib.iati_datastore_utils import *
from lib.util_file import *
from definitions import ROOT_DIR

jordan_params = build_combined_query(
    recipient_country_codes=["JO"],
    fl=["*"])

num_results, docs = query_collection("activity", jordan_params, count_only=True)
output_path = os.path.join(ROOT_DIR, "data", "iati", "jordan_activities_all_fields.json")
write_json(docs, output_path)
```

This query retrieves approximately 9,000 activities with all available narrative fields (40+ text fields including titles, descriptions, sector information, and organizational details). The comprehensive field selection is crucial because refugee targeting information can appear in various narrative elements beyond just the main description.

### 2. Classifying Refugee-Related Activities

The classification step uses DSPy (Declarative Self-improving Language Programs) with Google's Gemini models to automatically identify which activities target refugees and extract key characteristics. This addresses the core challenge: manually reviewing 9,000 activities would take months, but automated classification can process them in hours while maintaining high accuracy.

The `dspy_run.py` pipeline implements a sophisticated classification system that:
- **Identifies refugee nationalities** (Syrian, Palestinian, Iraqi, etc.) when explicitly mentioned as beneficiaries
- **Distinguishes target populations** (refugees vs. host communities vs. general population)
- **Extracts geographic settings** (camp, urban, rural) and specific locations
- **Categorizes the humanitarian-development nexus** (emergency response vs. capacity building)
- **Maps organizational relationships** (funders and implementers)

The model achieves 91.8% weighted accuracy, with perfect performance on refugee nationality identification - critical for understanding which populations receive assistance.

### 3. Filtering the Activities Dataset

After classification, we apply strategic filters to focus on the most relevant activities for refugee funding analysis:

```py
df = load_data()
df = filter_syria_ref_activities(df)
df = filter_duplicates(df)
```

**Syrian Refugee Focus**: The `filter_syria_ref_activities()` function identifies activities that specifically target Syrian refugees or mixed refugee populations. This filtering is essential because Jordan hosts multiple refugee populations (Palestinian, Iraqi, Yemeni), but our analysis focuses on the Syrian refugee response since 2011.

**Deduplication**: The `filter_duplicates()` function removes duplicate activities that appear multiple times due to how we query the IATI Datastore API. Activities can be duplicated when they appear in multiple query results (e.g., both as Jordan recipients and in transaction-level targeting).

This filtering reduces the dataset from ~9,000 total activities to ~2,000 Syrian refugee-related activities, creating a focused dataset for financial analysis.

### 4. Retrieving Transaction Data

For each refugee-related activity, we extract detailed financial transaction data to understand actual funding flows rather than just planned budgets:

```py
path = build_transaction_csv_from_datastore(iati_ids)
```

This step retrieves transaction-level data including:
- **Transaction values and currencies** (commitments, disbursements, expenditures)
- **Transaction dates** (when funds were actually transferred)
- **Provider and receiver organizations** (who sent and received funds)
- **Transaction descriptions** (additional context about fund usage)

Transaction data is crucial because IATI activities often contain multiple transactions over several years, and actual disbursements frequently differ from initial commitments.

### 5. Converting Transaction Values to USD

The final step standardizes all financial data into USD for comparative analysis:

```py
tf = convert_all_to_usd(tf)
```

This conversion process handles the complexity of multi-currency aid flows by:
- **Matching transaction dates** to historical exchange rates from the Federal Reserve
- **Handling pegged currencies** (Jordanian Dinar, Saudi Riyal) with fixed rates
- **Applying nearest-date matching** for currencies with limited rate data
- **Validating conversions** through spot-checking mechanisms

The result is a clean dataset where all financial values are comparable in USD, enabling analysis of funding trends, donor contributions, and spending patterns across the Syrian refugee response in Jordan.

This pipeline transforms fragmented, multi-language, multi-currency aid data into a structured dataset ready for analysis of refugee funding flows, organizational relationships, and geographic distribution of assistance.

## Data Sources

Understanding aid flows to Syrian refugees requires integrating multiple data sources that each provide essential but incomplete pieces of the funding puzzle. No single source captures the full scope of assistance, making data integration critical for comprehensive analysis.

### Primary Sources

**IATI Datastore** - The foundation for bilateral and multilateral aid tracking
- **Purpose**: Captures detailed aid activities from 200+ donors and implementers with rich narrative descriptions
- **Coverage**: ~9,000 aid activities in Jordan (current through Jun 2025) including bilateral, multilateral, and NGO funding
- **Unique Value**: Only source with detailed narrative descriptions enabling automated classification of refugee targeting
- **Limitations**: Voluntary reporting standard with variable data quality; some major donors underrepresent certain funding channels
- **API Access**: https://iatistandard.org/en/iati-tools-and-resources/iati-datastore/

**Federal Reserve Exchange Rate Data** - Essential for multi-currency financial analysis
- **Purpose**: Converts all financial flows to comparable USD values using historically accurate exchange rates
- **Coverage**: Daily exchange rates for major currencies (2010-2025) plus special handling for pegged currencies
- **Unique Value**: Enables accurate temporal analysis of funding trends across different donor currencies
- **Limitations**: Some minor currencies require manual rate sourcing; exchange rate timing may not match exact transaction dates
- **Data Source**: https://www.federalreserve.gov/releases/h10/hist/

**UN OCHA Financial Tracking Service (FTS)** - Validation and humanitarian funding context
- **Purpose**: Provides comprehensive humanitarian funding data for cross-validation and gap analysis
- **Coverage**: Syrian Regional Refugee and Resilience Plan (3RP) funding 2013-2024 across all host countries
- **Unique Value**: Authoritative source for humanitarian funding with detailed appeal and sector breakdowns
- **Limitations**: Not as much detail regarding program activity as IATI. Doens't cover direct bilateral funding.
- **Data Access**: [Syrian 3RP Funding Data](https://fts.unocha.org/plans/1168/flows?f%5B0%5D=flowStatus%3Apaid)

**UNHCR Refugee Registration Data** - Population context for funding analysis
- **Purpose**: Provides official refugee population figures for calculating per-capita funding and understanding demographic trends
- **Coverage**: Monthly registered Syrian refugee populations in Jordan (2012-2024)
- **Unique Value**: Only authoritative source for refugee population denominators in funding efficiency analysis
- **Limitations**: Registered refugees may undercount total refugee population; doesn't capture host community demographics
- **Data Access**: [UNHCR Jordan Refugee Data](https://data.unhcr.org/en/situations/syria/location/36)


### Known Limitations

**Reporting Gaps**: Some bilateral funding channels and private donations may be underrepresented in IATI
**Currency Timing**: Exchange rate matching uses nearest-date approximation which may introduce minor inaccuracies
**Population Undercounting**: UNHCR figures represent registered refugees only; actual refugee populations may be higher
**Classification Scope**: Automated classification focuses on explicit refugee targeting; indirect benefits to refugees may be missed

## Model Performance

Current performance on validation set (80/20 split):

### Overall Metrics
- **Weighted Accuracy**: 91.8% (prioritizing critical fields)
- **Simple Accuracy**: 86.9% (unweighted average across all fields)

### Field-Specific Performance
- **Refugee Group Identification**: 100.0% (perfect classification of refugee nationalities)
- **Target Population**: 91.3% (excellent refugee vs. host community distinction)  
- **Geographic Settings**: 89.1% (strong camp/urban/rural classification)
- **Geographic Focus**: 85.6% (reliable location extraction)
- **Humanitarian/Development Nexus**: 95.7% (excellent nexus understanding)
- **Funding Organizations**: 70.7% (good performance despite naming variations)
- **Implementing Organizations**: 76.5% (solid performance with organizational complexity)

### Key Insights
- **Exceptional Performance**: Perfect refugee nationality identification and excellent nexus classification
- **Strong Performance**: Target population and geographic setting classification exceed 89%
- **Organizational Challenges**: Lower scores on funding/implementing orgs likely due to naming variations (e.g., "USAID" vs "US Agency for International Development")
- **Model Robustness**: High weighted score (91.8%) demonstrates strong performance on priority classification tasks
- **Data Quality Impact**: Consistent high performance across narrative completeness levels


### Contact

For questions about the methodology, data access, or collaboration opportunities:
- **Technical Issues**: [Create GitHub issue]
- **Research Collaboration**: [Contact information]
- **Data Requests**: [Contact information]

---

**Note**: This project is designed for research and analysis purposes. Classification results should be validated by domain experts before use in operational decision-making.
