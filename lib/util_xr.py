import os
import pandas as pd
import numpy as np

from definitions import ROOT_DIR
from IPython import embed


def convert_all_to_usd(tf: pd.DataFrame):
    xr = pd.read_csv(os.path.join(ROOT_DIR, "data", "xr", "fed_xr_2010_2025.csv"))
    conversion_directions = xr.iloc[3].to_dict()  # conversion rate to usd or from usd
    conversion_directions.pop("Series Description")
    forex_to_usd = [
        currency
        for currency, direction in conversion_directions.items()
        if "$US" in direction
    ]
    usd_to_forex = [
        currency
        for currency, direction in conversion_directions.items()
        if "$US" not in direction
    ]
    # embed(banner1="pre slice")

    xr.columns = xr.iloc[2]
    xr = xr[5:]
    # embed(banner1="In XR Conversion")
    xr["date"] = pd.to_datetime(xr["Currency:"])
    date_dict = {}
    for _, row in xr.iterrows():
        date_dict[row["date"]] = row

    tf["closest_date"] = tf["date"].apply(
    # Convert ISO date format to match the exchange rate date format
    tf["date"] = pd.to_datetime(tf["transaction_value_value_date"]).dt.strftime(
        "%Y-%m-%d"
    )
        lambda x: find_closest_date(x, pd.Series(list(date_dict.keys())))
    )

    embed(banner1="In XR Conversion")
    tf["exchange_rate"] = tf.apply(
        lambda row: get_exchange_rate(row["closest_date"], row["currency"], date_dict),
        axis=1,
    )
    tf["transaction_value_usd"] = tf.apply(convert_to_usd, axis=1)
    embed(banner1="In XR Conversion")


def convert_to_usd(row):
    if row["currency"] == "USD":
        return row["transaction_value"]
    else:
        return row["transaction_value"] / row["exchange_rate"]


def get_exchange_rate(date, currency, date_dict):
    closest_date = find_closest_date(date, pd.Series(list(date_dict.keys())))

    rate_row = date_dict[closest_date]

    rate = rate_row.get(currency)

    if pd.isna(rate):
        print(
            f"Warning: No exchange rate available for {currency} on date {closest_date}"
        )
        return None

    return rate


def find_closest_date(date, dates_array):
    date = pd.to_datetime(date)
    dates_array = pd.to_datetime(dates_array)

    date_np = date.to_numpy()
    dates_np = dates_array.to_numpy()

    closest_idx = np.abs(dates_np - date_np).argmin()

    return dates_array.iloc[closest_idx]
