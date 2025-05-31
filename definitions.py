import os
from dotenv import load_dotenv

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), "."))
load_dotenv(os.path.join(ROOT_DIR, ".env"))
IATI_API_KEY = os.getenv("IATI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
