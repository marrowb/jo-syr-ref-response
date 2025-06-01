from definitions import GEMINI_API_KEY
from lib.util_file import read_json
import pandas as pd

def get_activity_dataframe(json_file:str) -> pd.DataFrame:
    activities = read_json(json_file)
    

if __name__ == "__main__":
    df = get_activity_dataframe("../data/iati/jordan_activities.json")
