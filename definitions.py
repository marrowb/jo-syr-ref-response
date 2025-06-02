import os

from dotenv import load_dotenv
from yaml import dump, load

try:
    from yaml import CDumper as Dumper
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Dumper, Loader

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), "."))
load_dotenv(os.path.join(ROOT_DIR, ".env"))
IATI_API_KEY = os.getenv("IATI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# DSPy Configuration
DSPY_CONFIG = {
    "strong_model": "gemini/gemini-2.5-pro-preview-05-06",
    "task_model": "gemini/gemini-2.0-flash",
    "sample_size": 100,
    "train_test_split": 0.8,
}

SECTOR_JSON_PATH = os.path.join(
    ROOT_DIR, "reference", "iati", "codelists", "json", "Sector.json"
)
RAW_ACTIVITIES = os.path.join(
    ROOT_DIR, "data", "iati", "jordan_activities_all_fields.json"
)

with open("./reference/iati/datastore.yaml", "r") as f:
    api_contract = load(f, Loader=Loader)
    DATASTORE_FIELDS = api_contract["components"]["schemas"][
        "Query_Response_All_IATI_Fields"
    ]["properties"]["response"]["properties"]["docs"]["items"]["properties"]

