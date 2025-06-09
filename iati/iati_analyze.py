import os
import random
from IPython import embed

import bigjson
import pandas as pd

from definitions import ROOT_DIR
from definitions import TRANSACTION_FIELDS
from lib.util_file import read_json
from lib.util_pandas import show_text_wrapped
from typing import List, Tuple, Dict, Any, Optional


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


def build_transaction_rows(iati_ids: List) -> pd.DataFrame:
    """Retrieve all the transactions for the given activities"""
    data_path = os.path.join(
        ROOT_DIR,
        "data",
        "iati",
        "jordan_activities_all_fields.json",
    )

    rows = []
    rows.append(["iati_identifier"].extend(TRANSACTION_FIELDS))
    with open(data_path, "rb") as f:
        j = bigjson.load(f)
        for _obj in j:
            if _obj["iati_identifier"] in iati_ids:
                data = extract_transactions_from_activity_json(_obj)
                if data:
                    rows.append(data)

    embed(banner1="Got all Transactions")
    return rows


def main():
    df = load_data()
    df = filter_syria_ref_activities(df)
    df = filter_duplicates(df)
    iati_ids = df["iati_identifier"].tolist()
    rows = build_transaction_rows(iati_ids)

    embed(banner1="End of Main")


if __name__ == "__main__":
    main()
