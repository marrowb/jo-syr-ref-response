import os, json
from lib.util_file import read_json
from typing import Dict
from definitions import ROOT_DIR

CODELIST_DIR = os.path.join(ROOT_DIR, "reference", "iati", "codelists")


def load_codelist(codetype: str) -> Dict:
    return read_json(os.path.join(CODELIST_DIR, "json", f"{codetype}.json"))

def search_description(codetype: str, query: str) -> Dict:
    codelist = load_codelist(codetype)['data']
    query = query.lower()
    results = []
    for _code in codelist: # _code includes code and metadata
        for k, v in _code.items():
            if k == "description" and query in v.lower():
                results.append(_code)
    return results