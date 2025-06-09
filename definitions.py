import os

from dotenv import load_dotenv

from lib.util_file import read_json

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), "."))
load_dotenv(os.path.join(ROOT_DIR, ".env"))
IATI_API_KEY = os.getenv("IATI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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

DATASTORE_FIELDS = read_json(
    os.path.join(ROOT_DIR, "data", "iati", "datastore_fields.json")
)

NARRATIVE_FIELDS = [
    field
    for field in DATASTORE_FIELDS
    if "narrative" in field and "xml_lang" not in field
]

TRANSACTION_FIELDS = [f for f in DATASTORE_FIELDS if "transaction" in f]

MLFLOW_SERVER_PORT = 5050
MLFLOW_SERVER_URI = f"http://127.0.0.1:{MLFLOW_SERVER_PORT}"
