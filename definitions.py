import os
from dotenv import load_dotenv

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), "."))
load_dotenv(os.path.join(ROOT_DIR, ".env"))
IATI_API_KEY = os.getenv("IATI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# DSPy Configuration
DSPY_CONFIG = {
    "strong_model": "gemini/gemini-2.5-pro-preview-05-06",
    "task_model": "gemini/gemini-2.0-flash", 
    "sample_size": 100,
    "train_test_split": 0.8
}

SECTOR_JSON_PATH = os.path.join(ROOT_DIR, "reference", "iati", "codelists", "json", "Sector.json")
