import pandas as pd
from ta.trend import SMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

def calculate_sma(ohlc_df: pd.DataFrame, window: int = 20) -> pd.Series:
    """
    Calculates Simple Moving Average (SMA).

    Args:
        ohlc_df: Pandas DataFrame with a 'close' column.
        window: The window period for SMA calculation.

    Returns:
        A pandas Series with SMA values. Returns an empty Series if input is invalid
        or data is insufficient.
    """
    if not isinstance(ohlc_df, pd.DataFrame) or 'close' not in ohlc_df.columns:
        print("Error: Input must be a pandas DataFrame with a 'close' column for SMA.")
        return pd.Series(dtype=float)
    if ohlc_df.empty:
        # print("Input DataFrame is empty for SMA.")
        return pd.Series(dtype=float)
    if len(ohlc_df) < window:
        # print(f"Insufficient data for SMA calculation (need {window}, got {len(ohlc_df)}).")
        # ta library will return NaNs, which is fine.
        pass

    try:
        indicator_sma = SMAIndicator(close=ohlc_df['close'], window=window, fillna=False)
        sma_series = indicator_sma.sma_indicator()
        return sma_series if sma_series is not None else pd.Series(dtype=float)
    except Exception as e:
        print(f"Error calculating SMA: {e}")
        return pd.Series(dtype=float)

def calculate_rsi(ohlc_df: pd.DataFrame, window: int = 14) -> pd.Series:
    """
    Calculates Relative Strength Index (RSI).

    Args:
        ohlc_df: Pandas DataFrame with a 'close' column.
        window: The window period for RSI calculation.

    Returns:
        A pandas Series with RSI values. Returns an empty Series if input is invalid
        or data is insufficient.
    """
    if not isinstance(ohlc_df, pd.DataFrame) or 'close' not in ohlc_df.columns:
        print("Error: Input must be a pandas DataFrame with a 'close' column for RSI.")
        return pd.Series(dtype=float)
    if ohlc_df.empty:
        # print("Input DataFrame is empty for RSI.")
        return pd.Series(dtype=float)
    if len(ohlc_df) < window + 1: # RSI needs at least window + 1 periods to get first valid value
        # print(f"Insufficient data for RSI calculation (need > {window}, got {len(ohlc_df)}).")
        # ta library will return NaNs.
        pass

    try:
        indicator_rsi = RSIIndicator(close=ohlc_df['close'], window=window, fillna=False)
        rsi_series = indicator_rsi.rsi()
        return rsi_series if rsi_series is not None else pd.Series(dtype=float)
    except Exception as e:
        print(f"Error calculating RSI: {e}")
        return pd.Series(dtype=float)

def calculate_bollinger_bands(ohlc_df: pd.DataFrame, window: int = 20, window_dev: int = 2) -> pd.DataFrame:
    """
    Calculates Bollinger Bands.

    Args:
        ohlc_df: Pandas DataFrame with a 'close' column.
        window: The window period for the moving average.
        window_dev: The number of standard deviations for the upper and lower bands.

    Returns:
        A pandas DataFrame with columns ['bb_upper', 'bb_middle', 'bb_lower'].
        Returns an empty DataFrame if input is invalid or data is insufficient.
    """
    if not isinstance(ohlc_df, pd.DataFrame) or 'close' not in ohlc_df.columns:
        print("Error: Input must be a pandas DataFrame with a 'close' column for Bollinger Bands.")
        return pd.DataFrame()
    if ohlc_df.empty:
        # print("Input DataFrame is empty for Bollinger Bands.")
        return pd.DataFrame()
    if len(ohlc_df) < window:
        # print(f"Insufficient data for Bollinger Bands (need {window}, got {len(ohlc_df)}).")
        # ta library will return NaNs.
        pass

    try:
        indicator_bb = BollingerBands(close=ohlc_df['close'], window=window, window_dev=window_dev, fillna=False)
        bb_df = pd.DataFrame()
        bb_df['bb_upper'] = indicator_bb.bollinger_hband()
        bb_df['bb_middle'] = indicator_bb.bollinger_mavg() # This is the SMA
        bb_df['bb_lower'] = indicator_bb.bollinger_lband()
        return bb_df
    except Exception as e:
        print(f"Error calculating Bollinger Bands: {e}")
        return pd.DataFrame()

def calculate_macd(ohlc_df: pd.DataFrame, window_slow: int = 26, window_fast: int = 12, window_sign: int = 9) -> pd.DataFrame:
    """
    Calculates Moving Average Convergence Divergence (MACD).

    Args:
        ohlc_df: Pandas DataFrame with a 'close' column.
        window_slow: The window for the slow moving average.
        window_fast: The window for the fast moving average.
        window_sign: The window for the signal line.

    Returns:
        A pandas DataFrame with columns ['macd_line', 'signal_line', 'macd_histogram'].
        Returns an empty DataFrame if input is invalid or data is insufficient.
    """
    if not isinstance(ohlc_df, pd.DataFrame) or 'close' not in ohlc_df.columns:
        print("Error: Input must be a pandas DataFrame with a 'close' column for MACD.")
        return pd.DataFrame()
    if ohlc_df.empty:
        # print("Input DataFrame is empty for MACD.")
        return pd.DataFrame()
    if len(ohlc_df) < window_slow: # MACD needs at least window_slow periods
        # print(f"Insufficient data for MACD (need {window_slow}, got {len(ohlc_df)}).")
        # ta library will return NaNs.
        pass

    try:
        indicator_macd = MACD(close=ohlc_df['close'],
                              window_slow=window_slow,
                              window_fast=window_fast,
                              window_sign=window_sign,
                              fillna=False)
        macd_df = pd.DataFrame()
        macd_df['macd_line'] = indicator_macd.macd()
        macd_df['signal_line'] = indicator_macd.macd_signal()
        macd_df['macd_histogram'] = indicator_macd.macd_diff() # Histogram = MACD Line - Signal Line
        return macd_df
    except Exception as e:
        print(f"Error calculating MACD: {e}")
        return pd.DataFrame()

if __name__ == '__main__':
    # Create a sample OHLC DataFrame for example usage
    # This would typically come from ohlc_list_to_dataframe(get_historical_ohlc(...))
    sample_data = {
        'timestamp': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05',
                                     '2023-01-06', '2023-01-07', '2023-01-08', '2023-01-09', '2023-01-10',
                                     '2023-01-11', '2023-01-12', '2023-01-13', '2023-01-14', '2023-01-15',
                                     '2023-01-16', '2023-01-17', '2023-01-18', '2023-01-19', '2023-01-20',
                                     '2023-01-21', '2023-01-22', '2023-01-23', '2023-01-24', '2023-01-25',
                                     '2023-01-26', '2023-01-27', '2023-01-28', '2023-01-29', '2023-01-30']),
        'open': [100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 110, 112, 111, 113, 115, 114, 116, 118, 117, 119, 120, 122, 121, 123, 125, 124, 126, 128, 127, 129],
        'high': [103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132],
        'low':  [99, 101, 100, 102, 103, 102, 104, 106, 105, 107, 108, 110, 109, 111, 112, 112, 114, 116, 115, 117, 118, 120, 119, 121, 122, 122, 124, 126, 125, 127],
        'close':[102, 101, 103, 105, 104, 106, 108, 107, 109, 110, 112, 111, 113, 115, 114, 116, 118, 117, 119, 120, 122, 121, 123, 125, 124, 126, 128, 127, 129, 130]
    }
    ohlc_example_df = pd.DataFrame(sample_data)
    ohlc_example_df.set_index('timestamp', inplace=True)

    print("--- SMA Example (window=5) ---")
    sma_values = calculate_sma(ohlc_example_df, window=5)
    print(sma_values.tail())

    print("\n--- RSI Example (window=14) ---")
    rsi_values = calculate_rsi(ohlc_example_df, window=14)
    print(rsi_values.tail())

    print("\n--- Bollinger Bands Example (window=20, dev=2) ---")
    bb_values = calculate_bollinger_bands(ohlc_example_df, window=20, window_dev=2)
    print(bb_values.tail())

    print("\n--- MACD Example (12, 26, 9) ---")
    macd_values = calculate_macd(ohlc_example_df, window_fast=12, window_slow=26, window_sign=9)
    print(macd_values.tail())

    print("\n--- Example with insufficient data for SMA (window=30 on 30 rows) ---")
    # The 'ta' library will produce NaNs for initial periods, but not necessarily an empty Series if some values can be calculated.
    # For SMA, first valid value is at index `window-1`.
    sma_insufficient = calculate_sma(ohlc_example_df.head(10), window=5) # 10 rows, window 5
    print(f"SMA with 10 rows, window 5 (some valid, some NaN):\n{sma_insufficient}")

    sma_very_insufficient = calculate_sma(ohlc_example_df.head(3), window=5) # 3 rows, window 5
    print(f"SMA with 3 rows, window 5 (all NaN):\n{sma_very_insufficient}")

    print("\n--- Example with empty DataFrame ---")
    empty_df_input = pd.DataFrame(columns=['open', 'high', 'low', 'close'])
    sma_empty = calculate_sma(empty_df_input)
    print(f"SMA from empty DataFrame is empty: {sma_empty.empty}")

    print("\n--- Example with missing 'close' column ---")
    no_close_df = ohlc_example_df[['open', 'high', 'low']]
    sma_no_close = calculate_sma(no_close_df)
    print(f"SMA from DataFrame without 'close' is empty: {sma_no_close.empty}")
