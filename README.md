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
- **Weighted Accuracy**: 78.5% (prioritizing critical fields)
- **Simple Accuracy**: 71.2% (unweighted average)

### Field-Specific Performance
- **Refugee Group Identification**: 85.3% (high precision for Syria, Palestine)
- **Target Population**: 72.1% (challenging refugee vs. host community distinction)  
- **Geographic Settings**: 68.9% (camp identification most accurate)
- **Geographic Focus**: 89.4% (strong location extraction)
- **Humanitarian/Development Nexus**: 76.8% (good nexus understanding)
- **Funding Organizations**: 45.2% (complex organizational relationships)
- **Implementing Organizations**: 38.7% (most challenging field)

### Key Insights
- **High Performance**: Refugee nationality and geographic extraction
- **Moderate Performance**: Population targeting and nexus classification  
- **Challenging Areas**: Organizational relationship mapping
- **Data Quality Impact**: Performance correlates with narrative completeness

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
