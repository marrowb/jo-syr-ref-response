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
    
    print(f"Processing {len(unique_currencies)} unique currencies: {list(unique_currencies)}")

    for currency in unique_currencies:
        print(f"\n--- Processing currency: {currency} ---")
        
        if currency == "USD":
            # USD transactions don't need exchange rates
            mask = tf_with_rates["currency"] == currency
            tf_with_rates.loc[mask, "exchange_rate"] = 1.0
            print(f"USD: Set {mask.sum()} transactions to rate 1.0")
            continue

        # Get transactions for this currency
        currency_mask = tf_with_rates["currency"] == currency
        currency_transactions = tf_with_rates[currency_mask].copy()
        
        if len(currency_transactions) == 0:
            continue
            
        print(f"Found {len(currency_transactions)} transactions for {currency}")
        
        # Show sample transaction dates
        sample_dates = currency_transactions["date"].dropna().sort_values()
        if len(sample_dates) > 0:
            print(f"Transaction date range: {sample_dates.iloc[0]} to {sample_dates.iloc[-1]}")
            print(f"Sample transaction dates: {sample_dates.head(3).tolist()}")

        # Check if currency has special handling
        if currency in special_rates:
            print(f"Using special rates for {currency}")
            rate_data = special_rates[currency].reset_index()
            
            # Debug rate data
            print(f"Special rate data shape: {rate_data.shape}")
            print(f"Rate date range: {rate_data['date'].min()} to {rate_data['date'].max()}")
            
            # Ensure both dataframes are properly sorted and have compatible dtypes
            currency_transactions_sorted = currency_transactions.sort_values("date").copy()
            rate_data_sorted = rate_data.sort_values("date").copy()
            
            # Ensure datetime types are compatible
            currency_transactions_sorted["date"] = pd.to_datetime(currency_transactions_sorted["date"])
            rate_data_sorted["date"] = pd.to_datetime(rate_data_sorted["date"])
            
            # Use manual merge instead of merge_asof for reliable nearest date matching
            merged = manual_nearest_date_merge(
                currency_transactions_sorted,
                rate_data_sorted,
                date_col="date",
                rate_col="rate"
            )

            # Update exchange rates using the original index
            tf_with_rates.loc[currency_mask, "exchange_rate"] = merged["rate"].values

        elif currency in currency_data.columns:
            print(f"Using Federal Reserve data for {currency}")
            # Use Federal Reserve data
            rate_data = currency_data[[currency]].dropna().reset_index()
            rate_data = rate_data.rename(columns={currency: "rate"})
            
            # Debug rate data
            print(f"Fed rate data shape: {rate_data.shape}")
            if len(rate_data) > 0:
                print(f"Rate date range: {rate_data['date'].min()} to {rate_data['date'].max()}")
                print(f"Sample rates: {rate_data.head(3)[['date', 'rate']].to_dict('records')}")

            # Ensure both dataframes are properly sorted and have compatible dtypes
            currency_transactions_sorted = currency_transactions.sort_values("date").copy()
            rate_data_sorted = rate_data.sort_values("date").copy()
            
            # Ensure datetime types are compatible
            currency_transactions_sorted["date"] = pd.to_datetime(currency_transactions_sorted["date"])
            rate_data_sorted["date"] = pd.to_datetime(rate_data_sorted["date"])

            # Use manual merge instead of merge_asof for reliable nearest date matching
            merged = manual_nearest_date_merge(
                currency_transactions_sorted,
                rate_data_sorted,
                date_col="date",
                rate_col="rate"
            )

            # Update exchange rates using the original index
            tf_with_rates.loc[currency_mask, "exchange_rate"] = merged["rate"].values

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


def manual_nearest_date_merge(transactions_df, rate_data_df, date_col="date", rate_col="rate"):
    """
    Alternative to merge_asof that manually finds the nearest date for each transaction.
    Use this if merge_asof continues to have issues.
    
    Args:
        transactions_df (pd.DataFrame): Transaction data with date column
        rate_data_df (pd.DataFrame): Rate data with date and rate columns
        date_col (str): Name of date column
        rate_col (str): Name of rate column
        
    Returns:
        pd.DataFrame: Transactions with rate column added
    """
    result_df = transactions_df.copy()
    result_df[rate_col] = np.nan
    
    # Convert to numpy arrays for faster searching
    rate_dates = pd.to_datetime(rate_data_df[date_col]).values
    rate_values = rate_data_df[rate_col].values
    
    for idx, row in transactions_df.iterrows():
        trans_date = pd.to_datetime(row[date_col])
        
        # Find the closest date
        date_diffs = np.abs((rate_dates - trans_date).astype('timedelta64[D]').astype(int))
        closest_idx = np.argmin(date_diffs)
        
        result_df.loc[idx, rate_col] = rate_values[closest_idx]
        
        # Debug output for first few transactions
        if idx < 3:
            closest_date = rate_dates[closest_idx]
            days_diff = date_diffs[closest_idx]
            print(f"Manual merge: {trans_date.date()} -> {pd.to_datetime(closest_date).date()} "
                  f"(rate: {rate_values[closest_idx]:.6f}, {days_diff} days diff)")
    
    return result_df


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

    # Debug exchange rate matching
    print("\nRunning exchange rate debug check...")
    spot_check_sample_transactions(tf_final, standardized_xr, n_samples=5)

    return tf_final


# Validation Functions


def debug_merge_results(transactions_df, rate_data_df, merged_df, currency):
    """
    Debug the merge_asof results by showing what dates were matched.
    
    Args:
        transactions_df (pd.DataFrame): Original transaction data (sorted)
        rate_data_df (pd.DataFrame): Rate data used for merge (sorted)
        merged_df (pd.DataFrame): Result of merge_asof
        currency (str): Currency being processed
    """
    print(f"  Debug merge for {currency}:")
    
    # Show a few examples of what got matched
    sample_size = min(3, len(merged_df))
    for i in range(sample_size):
        trans_date = merged_df.iloc[i]["date"]
        matched_rate = merged_df.iloc[i]["rate"]
        
        # Find what the actual closest rate should be
        rate_dates = rate_data_df["date"]
        closest_idx = (rate_dates - trans_date).abs().idxmin()
        actual_closest_date = rate_data_df.loc[closest_idx, "date"]
        actual_closest_rate = rate_data_df.loc[closest_idx, "rate"]
        
        print(f"    Transaction {i+1}: {trans_date}")
        print(f"      Merged rate: {matched_rate:.6f}")
        print(f"      Actual closest: {actual_closest_rate:.6f} (from {actual_closest_date})")
        
        if abs(matched_rate - actual_closest_rate) > 1e-6:
            print(f"      ⚠️  MISMATCH! Difference: {abs(matched_rate - actual_closest_rate):.6f}")
        else:
            print(f"      ✓ Match confirmed")


def spot_check_sample_transactions(tf_with_conversions, standardized_xr_data, n_samples=5):
    """
    Display sample conversions with intermediate steps for manual verification.
    Validates that merge_asof operation worked correctly by comparing merged rates
    with actual closest rates from source data.

    Args:
        tf_with_conversions (pd.DataFrame): Transaction data with conversions applied
        standardized_xr_data (pd.DataFrame): Standardized exchange rate data (usd per forex)
        n_samples (int): Number of samples to display
    """
    print("=== Spot Check Sample Transactions ===")
    print("Validating merge_asof accuracy and conversion formulas...\n")

    # Load special rates for comparison
    special_rates = create_special_currency_rates()

    # Sample different currencies if possible
    sample_df = tf_with_conversions.dropna(
        subset=["exchange_rate", "transaction_value_usd"]
    ).sample(n=min(n_samples, len(tf_with_conversions)))

    tolerance = 1e-6  # Small tolerance for floating point comparison

    for i, (_, row) in enumerate(sample_df.iterrows(), 1):
        print(f"--- Sample {i}/{len(sample_df)} ---")
        print(f"Transaction ID: {row.get('iati_identifier', 'Unknown')}")
        print(f"Date: {row['date']}")
        print(f"Currency: {row['currency']}")
        print(f"Original Value: {row['transaction_value']:.2f} {row['currency']}")
        print(f"Merged Exchange Rate: {row['exchange_rate']:.6f}")
        
        # Find the actual closest exchange rate from source data
        actual_rate = None
        rate_source = "Unknown"
        
        if row['currency'] == 'USD':
            actual_rate = 1.0
            rate_source = "USD (no conversion needed)"
        elif row['currency'] in special_rates:
            # Handle special currencies
            rate_source = f"Special rate ({row['currency']})"
            special_df = special_rates[row['currency']].reset_index()
            
            # Find closest date using merge_asof
            temp_df = pd.DataFrame({'date': [row['date']]})
            merged = pd.merge_asof(
                temp_df.sort_values('date'),
                special_df.sort_values('date'),
                on='date',
                direction='nearest'
            )
            actual_rate = merged['rate'].iloc[0] if not merged.empty else None
            
        elif row['currency'] in standardized_xr_data.columns:
            # Handle Federal Reserve data
            rate_source = f"Federal Reserve ({row['currency']})"
            rate_data = standardized_xr_data[[row['currency']]].dropna().reset_index()
            rate_data = rate_data.rename(columns={row['currency']: 'rate'})
            
            # Find closest date using merge_asof
            temp_df = pd.DataFrame({'date': [row['date']]})
            merged = pd.merge_asof(
                temp_df.sort_values('date'),
                rate_data.sort_values('date'),
                on='date',
                direction='nearest'
            )
            actual_rate = merged['rate'].iloc[0] if not merged.empty else None
        
        # Compare rates with enhanced debugging
        if actual_rate is not None:
            print(f"Actual Closest Rate: {actual_rate:.6f} (from {rate_source})")
            rate_match = abs(row['exchange_rate'] - actual_rate) < tolerance
            print(f"Rate Match: {'✓ YES' if rate_match else '✗ NO'}")
            if not rate_match:
                print(f"  Difference: {abs(row['exchange_rate'] - actual_rate):.8f}")
                
                # Additional debugging for mismatches
                if row['currency'] in standardized_xr_data.columns:
                    # Show nearby rates to understand the mismatch
                    rate_data = standardized_xr_data[[row['currency']]].dropna()
                    trans_date = row['date']
                    
                    # Find rates within +/- 7 days
                    date_diff = (rate_data.index - trans_date).days
                    nearby_mask = abs(date_diff) <= 7
                    nearby_rates = rate_data[nearby_mask]
                    
                    if len(nearby_rates) > 0:
                        print(f"  Nearby rates (±7 days):")
                        for date, rate_val in nearby_rates.iterrows():
                            days_diff = (date - trans_date).days
                            print(f"    {date.date()}: {rate_val.iloc[0]:.6f} ({days_diff:+d} days)")
        else:
            print(f"Actual Closest Rate: NOT FOUND (from {rate_source})")
            print("Rate Match: ✗ NO - Missing source data")
        
        # Validate conversion formula
        print(f"Converted USD Value: ${row['transaction_value_usd']:.2f}")
        
        if row['currency'] == 'USD':
            expected_usd = row['transaction_value']
            print(f"Expected USD (no conversion): ${expected_usd:.2f}")
        else:
            # Since rates are usd_per_forex: foreign_amount * rate = usd_amount
            expected_usd = row['transaction_value'] * row['exchange_rate']
            print(f"Manual Calculation: {row['transaction_value']:.2f} * {row['exchange_rate']:.6f} = ${expected_usd:.2f}")
        
        conversion_match = abs(row['transaction_value_usd'] - expected_usd) < tolerance
        print(f"Conversion Match: {'✓ YES' if conversion_match else '✗ NO'}")
        
        if not conversion_match:
            print(f"  Difference: ${abs(row['transaction_value_usd'] - expected_usd):.6f}")
        
        print()  # Empty line for readability
    
    print("=== Spot Check Complete ===")


