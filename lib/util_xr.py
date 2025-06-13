import os
import pandas as pd
import numpy as np

from definitions import ROOT_DIR, JOD_PEGGED_USD, SAR_PEGGED_USD


def load_and_prepare_exchange_rates():
    """Load Federal Reserve exchange rate data and prepare it for use."""
    xr = pd.read_csv(os.path.join(ROOT_DIR, "data", "xr", "fed_xr_2010_2025.csv"))

    conversion_directions = dict(zip(xr.iloc[2], xr.iloc[3]))
    conversion_directions.pop("Currency:", None)

    xr.columns = xr.iloc[2]
    xr = xr[5:].copy()
    xr["date"] = pd.to_datetime(xr["Currency:"])
    xr = xr.set_index("date").drop(columns=["Currency:"])

    for col in xr.columns:
        xr[col] = pd.to_numeric(xr[col], errors="coerce")

    return xr, conversion_directions


def standardize_xr_data_usd_per_forex(xr_df, conversion_directions):
    """Convert all exchange rates to usd_per_forex format (1 foreign currency = X USD)."""
    standardized_xr = xr_df.copy()

    for currency, direction in conversion_directions.items():
        if "$US" not in str(direction) and currency in standardized_xr.columns:
            # Take reciprocal for forex_per_usd rates
            standardized_xr[currency] = 1 / standardized_xr[currency]

    return standardized_xr


def prepare_transaction_dates(tf):
    """Convert transaction dates to timezone-naive datetime for merging."""
    tf_prepared = tf.copy()
    tf_prepared["date"] = pd.to_datetime(tf_prepared["transaction_value_value_date"])

    if tf_prepared["date"].dt.tz is not None:
        tf_prepared["date"] = tf_prepared["date"].dt.tz_localize(None)

    return tf_prepared


def create_special_currency_rates():
    """Create exchange rate data for currencies not in Federal Reserve data."""
    special_rates = {}
    date_range = pd.date_range("2010-01-01", "2025-12-31", freq="D")

    # Pegged currencies
    special_rates["JOD"] = pd.DataFrame(
        {"date": date_range, "rate": JOD_PEGGED_USD}
    ).set_index("date")

    special_rates["SAR"] = pd.DataFrame(
        {"date": date_range, "rate": SAR_PEGGED_USD}
    ).set_index("date")

    # CZK manual rates
    czk_data = {
        "2016-09-22": 0.0414,
        "2017-06-06": 0.0455,
        "2018-05-11": 0.0468,
        "2019-08-13": 0.043,
        "2021-07-01": 0.0463,
    }

    czk_df = (
        pd.DataFrame(
            [
                {"date": pd.to_datetime(date), "rate": rate}
                for date, rate in czk_data.items()
            ]
        )
        .set_index("date")
        .sort_index()
    )

    special_rates["CZK"] = czk_df
    return special_rates


def find_exchange_rates_for_currency(tf_prepared, currency_data, special_rates):
    """Find exchange rates for all transactions using nearest date matching."""
    tf_with_rates = tf_prepared.copy()
    tf_with_rates["exchange_rate"] = np.nan
    unique_currencies = tf_with_rates["currency"].dropna().unique()

    for currency in unique_currencies:
        currency_mask = tf_with_rates["currency"] == currency

        if currency == "USD":
            tf_with_rates.loc[currency_mask, "exchange_rate"] = 1.0
            continue

        currency_transactions = tf_with_rates[currency_mask].copy()
        if len(currency_transactions) == 0:
            continue

        if currency in special_rates:
            rate_data = special_rates[currency].reset_index()
        elif currency in currency_data.columns:
            rate_data = currency_data[[currency]].dropna().reset_index()
            rate_data = rate_data.rename(columns={currency: "rate"})
        else:
            print(f"Warning: No exchange rate data available for currency {currency}")
            continue

        # Sort and ensure compatible datetime types
        currency_transactions_sorted = currency_transactions.sort_values("date").copy()
        rate_data_sorted = rate_data.sort_values("date").copy()
        currency_transactions_sorted["date"] = pd.to_datetime(
            currency_transactions_sorted["date"]
        )
        rate_data_sorted["date"] = pd.to_datetime(rate_data_sorted["date"])

        merged = manual_nearest_date_merge(
            currency_transactions_sorted, rate_data_sorted, "date", "rate"
        )
        # embed(banner1=f"Merged currency: {currency}")

        tf_with_rates.loc[merged.index, "exchange_rate"] = merged["rate"].values

    return tf_with_rates


def apply_currency_conversions(tf_with_rates):
    """Apply USD conversions using standardized exchange rates."""
    tf_final = tf_with_rates.copy()

    # foreign_amount * exchange_rate = usd_amount (rates are usd_per_forex)
    tf_final["transaction_value_usd"] = np.where(
        tf_final["currency"] == "USD",
        tf_final["transaction_value"],
        tf_final["transaction_value"] * tf_final["exchange_rate"],
    )

    return tf_final


def manual_nearest_date_merge(
    transactions_df, rate_data_df, date_col="date", rate_col="rate"
):
    """Find nearest date for each transaction using manual search."""
    result_df = transactions_df.copy()
    result_df[rate_col] = np.nan

    rate_dates = pd.to_datetime(rate_data_df[date_col]).values
    rate_values = rate_data_df[rate_col].values

    for idx, row in transactions_df.iterrows():
        trans_date = pd.to_datetime(row[date_col]).to_numpy()
        date_diffs = np.abs(
            (rate_dates - trans_date).astype("timedelta64[D]").astype(int)
        )
        closest_idx = np.argmin(date_diffs)
        result_df.loc[idx, rate_col] = rate_values[closest_idx]

    return result_df


def spot_check_xr_matching(date, currency, expected_rate=None, tolerance=1e-6):
    """
    Verify exchange rate lookup for a specific date/currency combination.

    Args:
        date: Transaction date (string or datetime)
        currency: Currency code (e.g., 'EUR', 'JPY')
        expected_rate: Optional expected rate for validation
        tolerance: Acceptable difference for rate comparison

    Returns:
        dict: {'actual_rate': float, 'source': str, 'match': bool}
    """
    date = pd.to_datetime(date)

    if currency == "USD":
        return {"actual_rate": 1.0, "source": "USD", "match": True}

    # Load data sources
    xr_data, conversion_directions = load_and_prepare_exchange_rates()
    standardized_xr = standardize_xr_data_usd_per_forex(xr_data, conversion_directions)
    special_rates = create_special_currency_rates()

    actual_rate = None
    source = "Unknown"

    if currency in special_rates:
        source = f"Special rate ({currency})"
        rate_data = special_rates[currency].reset_index()
        temp_df = pd.DataFrame({"date": [date]})
        merged = pd.merge_asof(
            temp_df.sort_values("date"),
            rate_data.sort_values("date"),
            on="date",
            direction="nearest",
        )
        actual_rate = merged["rate"].iloc[0] if not merged.empty else None

    elif currency in standardized_xr.columns:
        source = f"Federal Reserve ({currency})"
        rate_data = standardized_xr[[currency]].dropna().reset_index()
        rate_data = rate_data.rename(columns={currency: "rate"})
        temp_df = pd.DataFrame({"date": [date]})
        merged = pd.merge_asof(
            temp_df.sort_values("date"),
            rate_data.sort_values("date"),
            on="date",
            direction="nearest",
        )
        actual_rate = merged["rate"].iloc[0] if not merged.empty else None

    match = False
    if expected_rate is not None and actual_rate is not None:
        match = abs(actual_rate - expected_rate) < tolerance

    return {"actual_rate": actual_rate, "source": source, "match": match}


def convert_all_to_usd(tf: pd.DataFrame):
    """Convert all transaction values to USD using vectorized operations."""
    xr_data, conversion_directions = load_and_prepare_exchange_rates()
    standardized_xr = standardize_xr_data_usd_per_forex(xr_data, conversion_directions)
    tf_prepared = prepare_transaction_dates(tf)
    special_rates = create_special_currency_rates()
    tf_with_rates = find_exchange_rates_for_currency(
        tf_prepared, standardized_xr, special_rates
    )
    tf_final = apply_currency_conversions(tf_with_rates)

    return tf_final
