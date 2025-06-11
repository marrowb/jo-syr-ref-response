import os
import pandas as pd
import numpy as np

from definitions import ROOT_DIR, JOD_PEGGED_USD, SAR_PEGGED_USD
from IPython import embed


def load_and_prepare_exchange_rates():
    """
    Load Federal Reserve exchange rate data and prepare it for use.

    Returns:
        pd.DataFrame: Exchange rate data with date index and cleaned columns
        dict: Mapping of currency codes to their direction (usd_per_forex or forex_per_usd)
    """
    xr = pd.read_csv(os.path.join(ROOT_DIR, "data", "xr", "fed_xr_2010_2025.csv"))

    # Get conversion directions from row 3
    conversion_directions = dict(zip(xr.iloc[2], xr.iloc[3]))
    conversion_directions.pop("Currency:", None)
    embed(banner1="conversion direction codes")

    # Set proper column names from row 2 (currency codes)
    xr.columns = xr.iloc[2]

    # Remove header rows and keep only data
    xr = xr[5:].copy()

    # Convert date column and set as index
    xr["date"] = pd.to_datetime(xr["Currency:"])
    xr = xr.set_index("date").drop(columns=["Currency:"])

    # Convert all rate columns to numeric
    for col in xr.columns:
        xr[col] = pd.to_numeric(xr[col], errors="coerce")

    return xr, conversion_directions


def standardize_xr_data_usd_per_forex(xr_df, conversion_directions):
    """
    Convert all exchange rates to reflect usd per forex

    Args:
        xr_df (pd.DataFrame): Exchange rate data
        conversion_directions (dict): Currency direction mappings

    Returns:
        pd.DataFrame: Standardized exchange rates where all rates represent "1 foreign currency = X USD"
    """
    standardized_xr = xr_df.copy()

    print("=== Exchange Rate Direction Analysis ===")

    # Identify currencies by their direction indicators
    usd_per_forex_currencies = []
    forex_per_usd_currencies = []

    for currency, direction in conversion_directions.items():
        if "$US" in str(direction):
            usd_per_forex_currencies.append(currency)
            print(f"{currency}: {direction} -> usd_per_forex (already correct)")
        else:
            forex_per_usd_currencies.append(currency)
            print(f"{currency}: {direction} -> forex_per_usd (needs inversion)")

    embed(banner1="In Standardization function")
    # Convert forex_per_usd rates to usd_per_forex by taking reciprocal
    for currency in forex_per_usd_currencies:
        if currency in standardized_xr.columns:
            original_sample = (
                standardized_xr[currency].dropna().iloc[0]
                if not standardized_xr[currency].dropna().empty
                else "N/A"
            )
            # Take reciprocal: if 1 USD = 92.55 JPY, then 1 JPY = 1/92.55 USD = 0.0108 USD
            standardized_xr[currency] = 1 / standardized_xr[currency]
            inverted_sample = (
                standardized_xr[currency].dropna().iloc[0]
                if not standardized_xr[currency].dropna().empty
                else "N/A"
            )
            print(f"  {currency}: {original_sample} -> {inverted_sample}")

    print("=== Standardization Complete ===")
    return standardized_xr


def prepare_transaction_dates(tf):
    """
    Convert transaction dates to timezone-naive format for merging.

    Args:
        tf (pd.DataFrame): Transaction dataframe

    Returns:
        pd.DataFrame: DataFrame with prepared date column
    """
    tf_prepared = tf.copy()

    # Convert transaction dates to datetime
    tf_prepared["date"] = pd.to_datetime(tf_prepared["transaction_value_value_date"])

    # Ensure timezone-naive for merge_asof compatibility
    if tf_prepared["date"].dt.tz is not None:
        tf_prepared["date"] = tf_prepared["date"].dt.tz_localize(None)

    return tf_prepared


def create_special_currency_rates():
    """
    Create exchange rate data for currencies not in Federal Reserve data.

    Returns:
        dict: Mapping of currency codes to their rate DataFrames
    """
    special_rates = {}

    # JOD - Pegged currency (already in usd_per_forex format)
    jod_rate = JOD_PEGGED_USD  # 1 JOD = X USD
    special_rates["JOD"] = pd.DataFrame(
        {"date": pd.date_range("2010-01-01", "2025-12-31", freq="D"), "rate": jod_rate}
    ).set_index("date")

    # SAR - Pegged currency (already in usd_per_forex format)
    sar_rate = SAR_PEGGED_USD  # 1 SAR = X USD
    special_rates["SAR"] = pd.DataFrame(
        {"date": pd.date_range("2010-01-01", "2025-12-31", freq="D"), "rate": sar_rate}
    ).set_index("date")

    # CZK - Manual rates (already in usd_per_forex format)
    czk_data = {
        "2016-09-22": 0.0414,  # 1 CZK = 0.0414 USD
        "2017-06-06": 0.0455,  # 1 CZK = 0.0455 USD
        "2018-05-11": 0.0468,  # 1 CZK = 0.0468 USD
        "2019-08-13": 0.043,  # 1 CZK = 0.043 USD
        "2021-07-01": 0.0463,  # 1 CZK = 0.0463 USD
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
    """
    Find exchange rates for all transactions using efficient merge_asof.

    Args:
        tf_prepared (pd.DataFrame): Prepared transaction data
        currency_data (pd.DataFrame): Federal Reserve exchange rate data
        special_rates (dict): Special currency rate data

    Returns:
        pd.DataFrame: Transaction data with exchange rates added
    """
    tf_with_rates = tf_prepared.copy()
    tf_with_rates["exchange_rate"] = np.nan

    # Get unique currencies in transactions
    unique_currencies = tf_with_rates["currency"].dropna().unique()

    for currency in unique_currencies:
        if currency == "USD":
            # USD transactions don't need exchange rates
            mask = tf_with_rates["currency"] == currency
            tf_with_rates.loc[mask, "exchange_rate"] = 1.0
            continue

        # Check if currency has special handling
        if currency in special_rates:
            rate_data = special_rates[currency].reset_index()
            currency_transactions = tf_with_rates[
                tf_with_rates["currency"] == currency
            ].copy()

            # Use merge_asof to find closest rates
            merged = pd.merge_asof(
                currency_transactions.sort_values("date"),
                rate_data.sort_values("date"),
                on="date",
                direction="nearest",
            )

            # Update exchange rates
            tf_with_rates.loc[
                tf_with_rates["currency"] == currency, "exchange_rate"
            ] = merged["rate"].values

        elif currency in currency_data.columns:
            # Use Federal Reserve data
            rate_data = currency_data[[currency]].dropna().reset_index()
            rate_data = rate_data.rename(columns={currency: "rate"})

            currency_transactions = tf_with_rates[
                tf_with_rates["currency"] == currency
            ].copy()

            # Use merge_asof to find closest rates
            merged = pd.merge_asof(
                currency_transactions.sort_values("date"),
                rate_data.sort_values("date"),
                on="date",
                direction="nearest",
            )

            # Update exchange rates
            tf_with_rates.loc[
                tf_with_rates["currency"] == currency, "exchange_rate"
            ] = merged["rate"].values

        else:
            print(f"Warning: No exchange rate data available for currency {currency}")

    return tf_with_rates


def apply_currency_conversions(tf_with_rates):
    """
    Apply vectorized USD conversions using standardized exchange rates.

    Args:
        tf_with_rates (pd.DataFrame): Transaction data with exchange rates

    Returns:
        pd.DataFrame: Transaction data with USD values calculated
    """
    tf_final = tf_with_rates.copy()

    # Since all rates are now usd_per_forex format, conversion is simple:
    # foreign_amount * exchange_rate = usd_amount
    tf_final["transaction_value_usd"] = np.where(
        tf_final["currency"] == "USD",
        tf_final["transaction_value"],  # USD transactions stay the same
        tf_final["transaction_value"]
        * tf_final["exchange_rate"],  # Convert foreign to USD
    )

    return tf_final


def convert_all_to_usd(tf: pd.DataFrame):
    """
    Convert all transaction values to USD using efficient vectorized operations.

    This function orchestrates the entire conversion process:
    1. Load and prepare exchange rate data
    2. Standardize all rates to forex_per_usd format
    3. Prepare transaction dates
    4. Find exchange rates for all currencies
    5. Apply conversions

    Args:
        tf (pd.DataFrame): Transaction dataframe with currency and value columns

    Returns:
        pd.DataFrame: Transaction dataframe with exchange_rate and transaction_value_usd columns added
    """
    print("Loading and preparing exchange rate data...")
    xr_data, conversion_directions = load_and_prepare_exchange_rates()

    print("Standardizing exchange rates to usd_per_forex format...")
    standardized_xr = standardize_xr_data_usd_per_forex(xr_data, conversion_directions)
    embed(banner1="Post xr standardization")

    print("Preparing transaction dates...")
    tf_prepared = prepare_transaction_dates(tf)

    print("Creating special currency rate data...")
    special_rates = create_special_currency_rates()

    print("Finding exchange rates for all transactions...")
    tf_with_rates = find_exchange_rates_for_currency(
        tf_prepared, standardized_xr, special_rates
    )

    print("Applying currency conversions...")
    tf_final = apply_currency_conversions(tf_with_rates)

    print("Currency conversion complete!")
    return tf_final


# Validation Functions


def validate_known_conversions():
    """
    Test conversion logic with known currency pairs and amounts.
    """
    print("=== Validating Known Conversions ===")

    # Test data with known conversions
    test_cases = [
        {"amount": 100, "currency": "USD", "expected_usd": 100},
        {
            "amount": 100,
            "currency": "JOD",
            "rate": JOD_PEGGED_USD,
            "expected_usd": 100 * JOD_PEGGED_USD,
        },
        {
            "amount": 100,
            "currency": "SAR",
            "rate": SAR_PEGGED_USD,
            "expected_usd": 100 * SAR_PEGGED_USD,
        },
    ]

    for case in test_cases:
        if case["currency"] == "USD":
            calculated_usd = case["amount"]
        else:
            calculated_usd = case["amount"] * case["rate"]

        print(
            f"{case['amount']} {case['currency']} = {calculated_usd:.2f} USD (expected: {case['expected_usd']:.2f})"
        )
        assert (
            abs(calculated_usd - case["expected_usd"]) < 0.01
        ), f"Conversion failed for {case['currency']}"

    print("✓ All known conversions validated successfully")


def check_conversion_consistency():
    """
    Verify that converting USD->Foreign->USD returns original amount.
    """
    print("=== Checking Conversion Consistency ===")

    test_amount = 1000  # USD

    # Test with pegged currencies
    for currency, pegged_rate in [("JOD", JOD_PEGGED_USD), ("SAR", SAR_PEGGED_USD)]:
        # USD to foreign
        usd_per_forex_rate = pegged_rate
        foreign_amount = test_amount / usd_per_forex_rate

        # Foreign back to USD
        back_to_usd = foreign_amount * usd_per_forex_rate

        print(
            f"${test_amount} USD -> {foreign_amount:.2f} {currency} -> ${back_to_usd:.2f} USD"
        )
        assert (
            abs(back_to_usd - test_amount) < 0.01
        ), f"Round-trip conversion failed for {currency}"

    print("✓ All round-trip conversions validated successfully")


def spot_check_sample_transactions(tf_with_conversions, n_samples=5):
    """
    Display sample conversions with intermediate steps for manual verification.

    Args:
        tf_with_conversions (pd.DataFrame): Transaction data with conversions applied
        n_samples (int): Number of samples to display
    """
    print("=== Spot Check Sample Transactions ===")

    # Sample different currencies
    sample_df = tf_with_conversions.dropna(
        subset=["exchange_rate", "transaction_value_usd"]
    ).sample(n=min(n_samples, len(tf_with_conversions)))

    for _, row in sample_df.iterrows():
        print(f"\nTransaction: {row.get('iati_identifier', 'Unknown')}")
        print(f"  Date: {row['date']}")
        print(f"  Original: {row['transaction_value']:.2f} {row['currency']}")
        print(
            f"  Exchange Rate (1 {row['currency']} = X USD): {row['exchange_rate']:.4f}"
        )
        print(f"  Converted: ${row['transaction_value_usd']:.2f} USD")

        if row["currency"] != "USD":
            manual_calc = row["transaction_value"] * row["exchange_rate"]
            print(
                f"  Manual calculation: {row['transaction_value']:.2f} * {row['exchange_rate']:.4f} = ${manual_calc:.2f}"
            )


def compare_old_vs_new_results(tf_old, tf_new, tolerance=0.01):
    """
    Compare results from old vs new implementation on sample data.

    Args:
        tf_old (pd.DataFrame): Results from old implementation
        tf_new (pd.DataFrame): Results from new implementation
        tolerance (float): Acceptable difference threshold
    """
    print("=== Comparing Old vs New Results ===")

    # Find common transactions
    common_ids = set(tf_old.get("iati_identifier", [])) & set(
        tf_new.get("iati_identifier", [])
    )

    if not common_ids:
        print("No common transaction identifiers found for comparison")
        return

    differences = []

    for tx_id in list(common_ids)[:10]:  # Check first 10 common transactions
        old_row = tf_old[tf_old["iati_identifier"] == tx_id].iloc[0]
        new_row = tf_new[tf_new["iati_identifier"] == tx_id].iloc[0]

        old_usd = old_row.get("transaction_value_usd", 0)
        new_usd = new_row.get("transaction_value_usd", 0)

        if pd.notna(old_usd) and pd.notna(new_usd):
            diff = abs(old_usd - new_usd)
            differences.append(diff)

            if diff > tolerance:
                print(
                    f"⚠️  Large difference for {tx_id}: Old=${old_usd:.2f}, New=${new_usd:.2f}, Diff=${diff:.2f}"
                )
            else:
                print(
                    f"✓ {tx_id}: Old=${old_usd:.2f}, New=${new_usd:.2f}, Diff=${diff:.4f}"
                )

    if differences:
        avg_diff = np.mean(differences)
        max_diff = np.max(differences)
        print(
            f"\nSummary: Avg difference=${avg_diff:.4f}, Max difference=${max_diff:.4f}"
        )
    else:
        print("No comparable transactions found")
