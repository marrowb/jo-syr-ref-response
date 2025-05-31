import csv
import json
import os
from typing import Any
from typing import Dict
from typing import List

from lib.util_datetime import datetime_serializer

"""
Read Functions
"""


def read_csv(
    path: str, delimiter: str = "\t", encoding: str = "latin-1"
) -> List[Dict]:
    with open(path, "r", encoding=encoding) as file:
        return list(csv.DictReader(file, delimiter=delimiter))



def read_json(path: str) -> Dict:
    return json.load(open(path, "r"))


"""
Write Functions
"""


def write_csv(data: Any, header: Any, filename: str) -> None:
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(header)
        # Write data
        writer.writerows(data)


def write_json(
    data: Any, filename: str, serializer=datetime_serializer
) -> None:
    with open(filename, "w", newline="") as file:
        json.dump(data, file, indent=4, ensure_ascii=False, default=serializer)
