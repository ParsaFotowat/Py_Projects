from typing import List, Dict, Any

def process_coin_data(coin_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Processes a list of coin data dictionaries to extract and standardize relevant information.

    Args:
        coin_data_list: A list of dictionaries, where each dictionary contains
                        information about a coin (e.g., from Coingecko API).

    Returns:
        A new list of dictionaries, each containing processed information:
        - id (string)
        - symbol (string, lowercased)
        - name (string)
        - trading_pair_spot (string, e.g., "BTCUSDT")
        Returns an empty list if the input is empty or if errors occur during processing.
    """
    if not coin_data_list:
        return []

    processed_coins = []
    for coin in coin_data_list:
        try:
            # Ensure coin is a dictionary before processing
            if not isinstance(coin, dict):
                print(f"Warning: Skipping non-dictionary item: {coin}")
                continue

            # Ensure essential keys are present
            coin_id = coin.get("id")
            symbol = coin.get("symbol")
            name = coin.get("name")

            if not all([coin_id, symbol, name]):
                print(f"Warning: Missing essential data for coin: {coin}. Skipping.")
                continue # Skip this coin if essential data is missing

            # Standardize symbol to lowercase
            symbol_lower = str(symbol).lower()

            # Create a common trading pair (e.g., BTCUSDT)
            # This might need to be more configurable in a real application
            trading_pair_spot = f"{symbol_lower.upper()}USDT"

            processed_coins.append({
                "id": str(coin_id),
                "symbol": symbol_lower,
                "name": str(name),
                "trading_pair_spot": trading_pair_spot
            })
        except Exception as e:
            # Catch any other unexpected errors during processing for a single coin
            # Ensure coin is a dict before trying to get 'id' in error message
            error_coin_id = coin.get('id', 'Unknown') if isinstance(coin, dict) else 'Unknown (non-dict item)'
            print(f"Error processing coin {error_coin_id}: {e}. Skipping.")
            continue

    return processed_coins


import pandas as pd

def ohlc_list_to_dataframe(ohlc_data: List[List[Any]], coin_id: str = "coin") -> pd.DataFrame:
    """
    Converts a list of lists OHLC data (from Coingecko) into a pandas DataFrame.

    Args:
        ohlc_data: List of lists, where each inner list is expected to be
                   [timestamp, open, high, low, close].
        coin_id: Identifier for the coin, used for potential multi-index or logging.

    Returns:
        A pandas DataFrame with columns ['timestamp', 'open', 'high', 'low', 'close'].
        'timestamp' is converted to datetime objects and set as the index.
        Returns an empty DataFrame if input is invalid or processing fails.
    """
    if not ohlc_data:
        # print(f"No OHLC data provided for {coin_id} to convert to DataFrame.")
        return pd.DataFrame()

    if not isinstance(ohlc_data, list) or not all(isinstance(item, list) and len(item) == 5 for item in ohlc_data):
        print(f"Error: Invalid OHLC data format for {coin_id}. Expected list of lists with 5 elements each.")
        return pd.DataFrame()

    try:
        df = pd.DataFrame(ohlc_data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)

        # Ensure numeric types for OHLC columns
        for col in ['open', 'high', 'low', 'close']:
            df[col] = pd.to_numeric(df[col], errors='coerce') # Coerce errors will turn non-numeric to NaT/NaN

        # Drop rows where essential OHLC data became NaN after coercion
        df.dropna(subset=['open', 'high', 'low', 'close'], inplace=True)

        return df
    except Exception as e:
        print(f"Error converting OHLC list to DataFrame for {coin_id}: {e}")
        return pd.DataFrame()

if __name__ == '__main__':
    # Example Usage for process_coin_data
    # ... (previous example code for process_coin_data can remain here) ...

    # Example Usage for ohlc_list_to_dataframe
    print("\n--- Example for ohlc_list_to_dataframe ---")
    sample_ohlc_list = [
        [1678886400000, 24000.0, 24500.0, 23800.0, 24200.0],
        [1678972800000, 24200.0, 25000.0, 24100.0, 24900.0],
        [1679059200000, 24900.0, 25200.0, 24700.0, 25100.0],
        [1679145600000, "invalid", 25500.0, 25000.0, 25300.0], # Example with non-numeric
    ]

    ohlc_df = ohlc_list_to_dataframe(sample_ohlc_list, coin_id="bitcoin_example")
    if not ohlc_df.empty:
        print("Successfully converted OHLC list to DataFrame:")
        print(ohlc_df.head())
        print(ohlc_df.info())
    else:
        print("Failed to convert OHLC list to DataFrame or list was empty/invalid.")

    print("\nConverting empty OHLC list:")
    empty_df = ohlc_list_to_dataframe([], coin_id="empty_example")
    print(f"DataFrame from empty list is empty: {empty_df.empty}")

    print("\nConverting invalid format OHLC list:")
    invalid_format_df = ohlc_list_to_dataframe([[1,2,3],[4,5]], coin_id="invalid_format_example")
    print(f"DataFrame from invalid format list is empty: {invalid_format_df.empty}")
