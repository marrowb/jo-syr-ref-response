import os
import csv
import random
from IPython import embed

import orjson
import pandas as pd

from definitions import ROOT_DIR
from definitions import TRANSACTION_FIELDS
from lib.util_file import read_json
from lib.util_pandas import show_text_wrapped
from lib.util_xr import *
from lib.iati_datastore_utils import query_collection, make_api_request
from typing import List, Set, Tuple, Dict, Any, Optional


def load_data():
    data_path = os.path.join(
        ROOT_DIR,
        "data",
        "iati",
        "batch-classify",
        "20250604_090728",
        "classified_results.json",
    )
    data = read_json(data_path)
    return pd.DataFrame.from_dict(data)


def filter_syria_ref_activities(df: pd.DataFrame) -> pd.DataFrame:
    # Filter only those activities potentially targeting Syrian Refugees
    return df[
        df["llm_ref_group"].map(
            lambda x: True
            if "Syria" in x or "mixed_or_unspecified_refugees" in x
            else False
        )
    ]


def spot_check(df: pd.DataFrame, narratives: List = None):
    """Spot check random elements in the data. Get llm fields, description, and title at a minimum."""
    ix = random.randrange(0, len(df))
    default = ["description_narrative", "title_narrative"]
    extra = []
    if narratives:
        for field in narratives:
            _extra = [k for k in df.columns if field in k]
            extra.extend(_extra)
        default.extend(extra)
    return {
        k: v for k, v in df.iloc[ix].to_dict().items() if k in default or "llm_" in k
    }


def filter_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """There are duplicate activities do to the way we hit the IATI Datastore API"""
    return df.drop_duplicates("iati_identifier")


def extract_transactions_from_activity_json(
    _obj: dict,
) -> Optional[List[Tuple[Any, ...]]]:
    iati_id = _obj["iati_identifier"]
    transaction_data = {field: _obj.get(field) for field in TRANSACTION_FIELDS}
    # transaction_data = {k: v for k, v in _obj.items() if k in TRANSACTION_FIELDS}

    transaction_lengths = {len(_list) for _list in transaction_data.values() if _list}
    if (
        len(transaction_lengths) == 0 or len(transaction_lengths) > 1
    ):  # no data or non-uniform data
        # print(f"Activity {iati_id} had non uniform data: \n {transaction_data}")
        return None

    transactions = []
    for i in range(transaction_lengths.pop()):
        transaction = [iati_id]
        for field in TRANSACTION_FIELDS:
            trans_field_list = transaction_data.get(field)
            try:
                transaction.append(trans_field_list[i])
            except (IndexError, TypeError):
                transaction.append(None)
        transactions.append(tuple(transaction))
    # embed(banner1="End of Extract Transactions")
    return transactions


def build_transaction_rows_from_all_activities_json(iati_ids: Set) -> pd.DataFrame:
    """Retrieve all the transactions for the given activities"""
    data_path = os.path.join(
        ROOT_DIR,
        "data",
        "iati",
        "jordan_activities_all_fields.json",
    )

    rows = []
    header = ["iati_identifier"] + TRANSACTION_FIELDS
    rows.append(header)

    with open(data_path, "rb") as f:
        objects = orjson.loads(f.read())
        i = 0
        for _obj in objects:
            if _obj["iati_identifier"] in iati_ids:
                data = extract_transactions_from_activity_json(_obj)
                if data:
                    rows.extend(data)
                    i += 1
                    print(f"Processed object {i}")

    df = pd.DataFrame(rows[1:], columns=rows[0])
    embed(banner1="Got all Transactions")
    return df


def build_transaction_csv_from_datastore(iati_ids: Set, batch_size: int = 100) -> str:
    """Build a CSV file of transactions from the IATI Datastore API"""

    output_path = os.path.join(ROOT_DIR, "data", "iati", "transactions.csv")
    iati_ids_list = list(iati_ids)

    # Write header first
    header_written = False

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = None

        for i in range(0, len(iati_ids_list), batch_size):
            batch_ids = iati_ids_list[i : i + batch_size]
            print(f"Processing batch {i//batch_size + 1}: {len(batch_ids)} IDs")

            # Build query
            quoted_ids = ['"' + id + '"' for id in batch_ids]
            or_clause = " OR ".join(quoted_ids)
            query_string = "iati_identifier:(" + or_clause + ")"

            query_params = {
                "q": query_string,
                "fl": ",".join(
                    ["iati_identifier", "default_currency"] + TRANSACTION_FIELDS
                ),
                "wt": "csv",
                "rows": 10000,  # Large number to get all results in batch
            }

            try:
                response = make_api_request(
                    "GET", "/transaction/select", params=query_params
                )
                csv_text = response.text

                # Parse CSV response
                # csv_reader = csv.reader(StringIO(csv_text))
                csv_reader = csv.reader(
                    response.text.split("\n"), delimiter=",", escapechar="\\"
                )
                rows = list(csv_reader)

                if not rows:
                    continue

                # Write header only once
                if not header_written:
                    writer = csv.writer(outfile)
                    writer.writerow(rows[0])  # Header row
                    header_written = True

                # Write data rows (skip header)
                if len(rows) > 1:
                    writer.writerows(rows[1:])

            except Exception as e:
                print(f"Error processing batch {i//batch_size + 1}: {e}")
                continue

    print(f"Transaction CSV written to: {output_path}")
    return output_path


def clean_iati_transaction_data(output_filename: str, iati_ids: Set) -> pd.DataFrame:
    tf = pd.read_csv(os.path.join(ROOT_DIR, "data", "iati", "transactions.csv"))
    tf = tf[
        tf["iati_identifier"].isin(iati_ids)
    ]  # Ensure we keep the transactions for refugee related activities
    tf["currency"] = tf["transaction_value_currency"].fillna(
        tf["default_currency"]
    )  # Use default currency where transaction level currency is unavailable

    tf.to_csv(os.path.join(ROOT_DIR, "data", "iati", output_filename))
    return tf


def main():
    df = load_data()
    df = filter_syria_ref_activities(df)
    df = filter_duplicates(df)

    iati_ids = set(df["iati_identifier"].tolist())

    # Uncomment these if you want to rebuild the transactions files
    # rows = build_transaction_rows_from_all_activities_json(iati_ids)
    # path = build_transaction_csv_from_datastore(iati_ids)

    tf = clean_iati_transaction_data("transactions_cleaned.csv", iati_ids)

    convert_all_to_usd(tf)

    embed(banner1="End of Main")


if __name__ == "__main__":
    main()
