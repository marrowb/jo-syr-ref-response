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
[Funding vs. Total Individuals]("./figures/contributions_vs_individuals.png")
[Funding per Refugees]("./figures/contributions_vs_individuals.png")


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

## Usage Examples

### Basic Classification

```python
import asyncio
from iati.dspy_run import setup_dspy_config, batch_classify, load_saved_model
from lib.util_file import read_json

# Setup DSPy configuration
setup_dspy_config()

# Load activities data
activities = read_json("data/iati/jordan_activities_narratives.json")

# Run batch classification
await batch_classify(
    model_path="models/aid_classifier_85_2024-12-15_14:30:22.json",
    activities=activities[:100],  # Process first 100 activities
    batch_size=10
)
```

### Training a New Model

```python
from iati.dspy_run import train_classification_model, setup_dspy_config
from lib.util_file import read_json

# Setup configuration and MLflow tracking
setup_dspy_config()

# Train model on human-labeled data
# Requires data/iati/model/jordan_activities_labeled.json
trained_model = train_classification_model()

# Model automatically saved with performance score and timestamp
print(f"Model saved with score: {trained_model.score}")
```

### Interactive Label Validation

```python
from lib.util_labels import LabelValidator

# Create validator instance
validator = LabelValidator()

# Review and correct model predictions
validator.review_activities(
    input_file="data/training_pre_human.json",
    output_file="data/training_corrected.json"
)

# Commands during review:
# 'e' - Edit current activity
# 'f 1' - Quick edit field 1 (refugee groups)
# 'notes' - Add notes about classification decisions
# 'unclear' - Mark activity as unclear/unrelated
# 'q' - Save and quit
```

### Currency Conversion Pipeline

```python
from iati.iati_build_usd_transactions import main as build_transactions
from lib.util_xr import convert_all_to_usd, spot_check_xr_matching
import pandas as pd

# Build USD transaction dataset
build_transactions()

# Spot check exchange rate accuracy
result = spot_check_xr_matching(
    date="2023-06-15", 
    currency="EUR", 
    expected_rate=1.0875
)
print(f"Rate check: {result}")
```

## IATI Datastore API Wrapper

This project includes a comprehensive wrapper for the IATI Datastore API that simplifies querying and data retrieval. The wrapper handles authentication, pagination, error handling, and provides convenient query builders for common use cases.

### Key Features

- **Session Management**: Configurable HTTP sessions with timeout and retry logic
- **Query Builders**: Helper functions for complex multi-field queries
- **Pagination Support**: Automatic handling of large result sets with `fetch_all=True`
- **Preview Mode**: Quick data exploration with `preview=True`
- **Count Queries**: Efficient result counting with `count_only=True`
- **Error Handling**: Robust exception handling and status code validation

### Basic Usage

```python
from lib.iati_datastore_utils import query_collection, build_combined_query

# Simple query for activities in Jordan
jordan_params = build_combined_query(
    recipient_country_codes=["JO"],
    fl=["iati_identifier", "title_narrative", "description_narrative"]
)

# Get count of matching activities
num_results, docs = query_collection("activity", jordan_params, count_only=True)
print(f"Found {num_results} activities")

# Preview first 5 results
num_results, docs = query_collection("activity", jordan_params, preview=True)

# Fetch all results (handles pagination automatically)
num_results, all_docs = query_collection("activity", jordan_params, fetch_all=True)
```

### Advanced Query Building

```python
# Complex multi-criteria query
complex_params = build_combined_query(
    recipient_country_codes=["JO", "LB", "TR"],  # Multiple countries
    sector_codes=["72010", "72040"],             # Emergency response sectors
    humanitarian_plan_codes=["HSDN18"],          # Specific humanitarian plan
    transaction_types=["D", "C"],                # Disbursements and commitments
    fl=["iati_identifier", "title_narrative", "sector_narrative", 
        "humanitarian_scope_narrative", "transaction_value"]
)

# Query with additional filters
params_with_filters = build_combined_query(
    recipient_country_codes=["JO"],
    additional_query_params='activity_status_code:"2"',  # Active activities only
    fl=["iati_identifier", "title_narrative", "activity_status_code"]
)
```

### Fetching Jordan Aid Activities

The project's core dataset was built by querying all aid activities where Jordan appears as either:
1. **Activity-level recipient country** (`recipient_country_code:"JO"`)
2. **Transaction-level recipient country** (`transaction_recipient_country_code:"JO"`)

This comprehensive approach captures both activities explicitly targeted at Jordan and those with individual transactions flowing to Jordan.

```python
# Query used to build the Jordan dataset
jordan_params = build_combined_query(
    recipient_country_codes=["JO"],  # Includes both activity and transaction level
    fl=[
        # Core identification
        "iati_identifier", "title_narrative", "description_narrative",
        
        # Activity metadata  
        "activity_status_code", "sector_code", "sector_narrative",
        
        # Humanitarian context
        "humanitarian_scope_type", "humanitarian_scope_code", 
        "humanitarian_scope_narrative",
        
        # Financial transactions
        "transaction_value", "transaction_value_currency", 
        "transaction_value_value_date", "transaction_transaction_type_code",
        
        # Organizational information
        "transaction_provider_org_ref", "transaction_provider_org_type",
        "transaction_provider_org_narrative", "transaction_transaction_date_iso_date"
    ]
)

# Execute the query
num_results, jordan_activities = query_collection(
    "activity", 
    jordan_params, 
    fetch_all=True
)

print(f"Retrieved {len(jordan_activities)} activities for Jordan")
# Result: 9,187 activities spanning 2010-2024
```

### API Wrapper Functions

#### Core Functions
- `query_collection()`: Main interface for querying activity, budget, or transaction collections
- `make_api_request()`: Low-level HTTP request handler with error handling
- `create_request_session()`: Configurable session factory for API requests

#### Query Builders
- `build_combined_query()`: Comprehensive query builder for multiple criteria
- `build_sector_query()`: DAC sector code queries
- `build_humanitarian_scope_query()`: Humanitarian plan and emergency queries  
- `build_recipient_country_query()`: Country-specific queries with transaction support
- `build_transaction_type_query()`: Filter by transaction types (disbursements, commitments, etc.)

#### Utility Functions
- `ping_api()`: Test API connectivity
- `check_identifiers()`: Validate IATI identifier existence
- `get_docs()` / `get_num_results()`: Extract data from API responses

### Error Handling and Rate Limiting

The wrapper includes robust error handling for common API issues:

```python
try:
    num_results, docs = query_collection("activity", params, fetch_all=True)
except requests.exceptions.RequestException as e:
    print(f"API request failed: {e}")
except ValueError as e:
    print(f"Invalid query parameters: {e}")
```

**Built-in Features:**
- Automatic retry logic for transient failures
- Rate limiting compliance (1000 rows per request max)
- Timeout handling (30 second default)
- Status code validation with meaningful error messages

### Data Validation

```python
# Verify data completeness
activities_with_narratives = [
    activity for activity in jordan_activities 
    if activity.get("title_narrative") or activity.get("description_narrative")
]

print(f"Activities with narrative content: {len(activities_with_narratives)}")
# Result: 100% of Jordan activities have at least title or description
```

## Data Sources

### Primary Sources
- **IATI Datastore**: 40+ narrative fields from aid activities in Jordan
- **Federal Reserve**: Daily exchange rates for major currencies (2010-2025)
- **OCHA FTS**: UN humanitarian funding data for validation and context

### Data Coverage
- **Activities**: ~9,000 aid activities in Jordan (2010-2024)
- **Transactions**: Financial flows with multi-currency support
- **Narratives**: Title, description, sector, organization, location, and result narratives
- **Organizations**: 200+ reporting and participating organizations

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

## Key Commands

### Main Pipeline Operations
```bash
# Start MLflow server and run full classification pipeline
python iati/dspy_run.py

# Build sample for human labeling (first step)
python -c "from iati.dspy_run import build_sample_for_labeling; build_sample_for_labeling()"

# Train model on labeled data
python -c "from iati.dspy_run import train_classification_model; train_classification_model()"
```

### Data Processing
```bash
# Build USD transaction dataset with exchange rate conversion
python iati/iati_build_usd_transactions.py

# Validate IATI API connectivity
python lib/iati_datastore_utils.py
```

### Label Management
```bash
# Validate existing labels for errors
python -m lib.util_labels validate data/iati/model/jordan_activities_labeled.json

# Interactive label correction and review
python -m lib.util_labels review data/training_pre_human.json data/training_corrected.json

# Show label statistics and distribution
python -m lib.util_labels stats data/training_corrected.json
```

### MLflow Tracking
```bash
# View experiment results (after starting MLflow server)
# Navigate to http://127.0.0.1:5050 in browser

# Compare model performance across runs
# Use MLflow UI to analyze metrics and failed predictions
```

## Configuration

Key settings in `definitions.py`:

### Model Configuration
```python
DSPY_CONFIG = {
    "strong_model": "gemini/gemini-2.5-pro-preview-05-06",  # Training
    "task_model": "gemini/gemini-2.0-flash",               # Inference  
    "sample_size": 100,                                    # Training sample
    "train_test_split": 0.8,                              # 80/20 split
}
```

### Processing Limits
- **Batch Size**: 10-50 activities per batch (rate limiting)
- **Concurrent Requests**: 10 simultaneous API calls
- **Retry Logic**: 3 attempts with exponential backoff
- **Progress Persistence**: Resume from interruptions

### Exchange Rate Configuration
- **Pegged Currencies**: JOD (1.41044 USD), SAR (0.26666 USD)
- **Data Source**: Federal Reserve H.10 series
- **Update Frequency**: Daily rates with nearest-date matching
- **Special Handling**: CZK manual rates for specific dates

## Contributing

### Adding New Classification Fields

1. **Update Classifier Signature** (`lib/dspy_classifier.py`):
```python
class IATIClassifier(dspy.Signature):
    # Add new output field
    llm_new_field: List[Literal["option1", "option2"]] = dspy.OutputField(
        desc="Detailed description of classification logic..."
    )
```

2. **Update Validation** (`lib/util_labels.py`):
```python
class LabelValidator:
    def __init__(self):
        self.valid_new_field = ["option1", "option2"]
        self.label_fields.append("llm_new_field")
```

3. **Update Metrics** (`lib/dspy_metrics.py`):
```python
# Add field to weighted_metric and field_specific_metrics
field_weights["llm_new_field"] = 2.0  # Set appropriate weight
```

### Improving Model Prompts

- **Field Descriptions**: Focus on explicit criteria and edge cases
- **Examples**: Include positive and negative examples in docstrings  
- **Constraints**: Use Literal types for controlled vocabularies
- **Logic**: Emphasize conservative classification to reduce false positives

### Data Validation Procedures

1. **Automated Validation**: Run `python -m lib.util_labels validate` on all datasets
2. **Human Review**: Use interactive validator for 10-20% sample validation
3. **Cross-validation**: Compare results across different model versions
4. **Domain Expert Review**: Engage humanitarian practitioners for edge cases

### Testing Requirements

- **Unit Tests**: Test individual utility functions and API clients
- **Integration Tests**: Validate end-to-end pipeline with sample data
- **Performance Tests**: Benchmark classification speed and accuracy
- **Data Quality Tests**: Verify exchange rate accuracy and API responses

## Troubleshooting

### Common Issues

**API Rate Limiting**:
```bash
# Reduce batch size in batch_classify()
await batch_classify(model_path="...", activities=data, batch_size=5)
```

**Memory Issues with Large Datasets**:
```python
# Process in smaller chunks
for i in range(0, len(activities), 1000):
    chunk = activities[i:i+1000]
    await batch_classify(model_path="...", activities=chunk)
```

**Exchange Rate Lookup Failures**:
```python
# Check specific currency/date combinations
from lib.util_xr import spot_check_xr_matching
result = spot_check_xr_matching("2023-01-15", "EUR")
print(result)
```

**MLflow Server Issues**:
```bash
# Kill existing MLflow processes
pkill -f "mlflow server"

# Restart with clean state
python iati/dspy_run.py
```

## License & Acknowledgments

### License
This project is licensed under the MIT License - see the LICENSE file for details.

### Acknowledgments

- **IATI Standard**: International Aid Transparency Initiative for open aid data standards
- **DSPy Framework**: Stanford NLP for the declarative programming framework  
- **Google Gemini**: Advanced language models enabling sophisticated classification
- **UNHCR & UNRWA**: Refugee data and context for validation
- **Federal Reserve**: Exchange rate data for accurate financial analysis

### Research Context

This project supports research on:
- Humanitarian aid effectiveness and coordination
- Refugee assistance funding flows and gaps
- Humanitarian-development nexus programming
- Aid transparency and accountability mechanisms

### Publications

*[Add relevant publications, conference presentations, or reports that use this work]*

### Contact

For questions about the methodology, data access, or collaboration opportunities:
- **Technical Issues**: [Create GitHub issue]
- **Research Collaboration**: [Contact information]
- **Data Requests**: [Contact information]

---

**Note**: This project is designed for research and analysis purposes. Classification results should be validated by domain experts before use in operational decision-making.
