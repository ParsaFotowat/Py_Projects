import unittest
import pandas as pd
import numpy as np # For NaN comparison and sample data
from trading_bot.analysis import technical_indicators as ti
from trading_bot.processing.data_processor import ohlc_list_to_dataframe # To create test DFs

class TestTechnicalIndicators(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create sample OHLC data for testing - 30 periods
        # More data than most indicator windows to ensure some valid calculations
        raw_ohlc_data = []
        for i in range(30):
            timestamp = 1678886400000 + (i * 86400000) # Daily data
            open_price = 100 + i * 0.5
            high_price = open_price + 5 + (i * 0.1)
            low_price = open_price - 3 - (i * 0.1)
            close_price = open_price + 2
            raw_ohlc_data.append([timestamp, open_price, high_price, low_price, close_price])

        cls.sample_ohlc_df = ohlc_list_to_dataframe(raw_ohlc_data, "sample_coin")

        # Create a very short DataFrame for insufficient data tests
        cls.short_ohlc_df = cls.sample_ohlc_df.head(5)

        # Create an empty DataFrame
        cls.empty_ohlc_df = pd.DataFrame(columns=['open', 'high', 'low', 'close'])


    # --- SMA Tests ---
    def test_calculate_sma_valid(self):
        window = 5
        sma_series = ti.calculate_sma(self.sample_ohlc_df, window=window)
        self.assertIsInstance(sma_series, pd.Series)
        self.assertFalse(sma_series.empty)
        self.assertEqual(len(sma_series), len(self.sample_ohlc_df))
        # First `window-1` values should be NaN
        self.assertTrue(sma_series.head(window - 1).isnull().all())
        self.assertFalse(sma_series.tail(1).isnull().any()) # Last value should not be NaN

    def test_calculate_sma_insufficient_data(self):
        # Window is larger than data length
        sma_series = ti.calculate_sma(self.short_ohlc_df, window=10)
        self.assertIsInstance(sma_series, pd.Series)
        # self.assertTrue(sma_series.empty) # ta library might return series of NaNs
        self.assertTrue(sma_series.isnull().all(), "SMA with insufficient data should be all NaNs or empty")


    def test_calculate_sma_empty_df(self):
        sma_series = ti.calculate_sma(self.empty_ohlc_df)
        self.assertIsInstance(sma_series, pd.Series)
        self.assertTrue(sma_series.empty)

    def test_calculate_sma_missing_close_column(self):
        df_no_close = self.sample_ohlc_df[['open', 'high', 'low']].copy()
        sma_series = ti.calculate_sma(df_no_close)
        self.assertIsInstance(sma_series, pd.Series)
        self.assertTrue(sma_series.empty)

    # --- RSI Tests ---
    def test_calculate_rsi_valid(self):
        window = 14
        rsi_series = ti.calculate_rsi(self.sample_ohlc_df, window=window)
        self.assertIsInstance(rsi_series, pd.Series)
        self.assertFalse(rsi_series.empty)
        self.assertEqual(len(rsi_series), len(self.sample_ohlc_df))
        # RSI typically has initial NaNs (window periods)
        # Based on observed output: first non-NaN is at index (window - 1)
        if window > 0:
             self.assertTrue(rsi_series.iloc[0:window-1].isnull().all(), f"RSI values from index 0 to {window-2} should be NaN")
             self.assertFalse(pd.isna(rsi_series.iloc[window-1]), f"RSI value at index {window-1} should not be NaN")

        self.assertFalse(pd.isna(rsi_series.iloc[window]), f"RSI value at index {window} should not be NaN") # Check next value too
        self.assertFalse(rsi_series.tail(1).isnull().any())
        # RSI values should be between 0 and 100
        self.assertTrue((rsi_series.dropna() >= 0).all() and (rsi_series.dropna() <= 100).all())

    def test_calculate_rsi_insufficient_data(self):
        # RSI needs more than `window` periods. For window 14, needs 15.
        rsi_series = ti.calculate_rsi(self.sample_ohlc_df.head(10), window=14) # 10 rows, window 14
        self.assertIsInstance(rsi_series, pd.Series)
        self.assertTrue(rsi_series.isnull().all())

    def test_calculate_rsi_empty_df(self):
        rsi_series = ti.calculate_rsi(self.empty_ohlc_df)
        self.assertIsInstance(rsi_series, pd.Series)
        self.assertTrue(rsi_series.empty)

    def test_calculate_rsi_missing_close_column(self):
        df_no_close = self.sample_ohlc_df[['open', 'high', 'low']].copy()
        rsi_series = ti.calculate_rsi(df_no_close)
        self.assertIsInstance(rsi_series, pd.Series)
        self.assertTrue(rsi_series.empty)

    # --- Bollinger Bands Tests ---
    def test_calculate_bollinger_bands_valid(self):
        window = 20
        bb_df = ti.calculate_bollinger_bands(self.sample_ohlc_df, window=window)
        self.assertIsInstance(bb_df, pd.DataFrame)
        self.assertFalse(bb_df.empty)
        self.assertEqual(len(bb_df), len(self.sample_ohlc_df))
        self.assertListEqual(list(bb_df.columns), ['bb_upper', 'bb_middle', 'bb_lower'])
        # Initial `window-1` rows for bb_middle (SMA) will be NaN
        self.assertTrue(bb_df['bb_middle'].head(window - 1).isnull().all())
        self.assertFalse(bb_df.tail(1).isnull().any().any()) # No NaNs in last row for any column
        # Upper band should be >= Middle band, Lower band should be <= Middle band
        self.assertTrue((bb_df['bb_upper'].dropna() >= bb_df['bb_middle'].dropna()).all())
        self.assertTrue((bb_df['bb_lower'].dropna() <= bb_df['bb_middle'].dropna()).all())


    def test_calculate_bollinger_bands_insufficient_data(self):
        bb_df = ti.calculate_bollinger_bands(self.short_ohlc_df, window=10) # 5 rows, window 10
        self.assertIsInstance(bb_df, pd.DataFrame)
        # self.assertTrue(bb_df.empty) # ta library returns df with all NaNs
        self.assertTrue(bb_df.isnull().all().all(), "BB with insufficient data should be all NaNs or empty")


    def test_calculate_bollinger_bands_empty_df(self):
        bb_df = ti.calculate_bollinger_bands(self.empty_ohlc_df)
        self.assertIsInstance(bb_df, pd.DataFrame)
        self.assertTrue(bb_df.empty)

    def test_calculate_bollinger_bands_missing_close_column(self):
        df_no_close = self.sample_ohlc_df[['open', 'high', 'low']].copy()
        bb_df = ti.calculate_bollinger_bands(df_no_close)
        self.assertIsInstance(bb_df, pd.DataFrame)
        self.assertTrue(bb_df.empty)

    # --- MACD Tests ---
    def test_calculate_macd_valid(self):
        window_slow = 26
        window_fast = 12
        # Need enough data for slow window + signal window for all values to be non-NaN potentially
        # Sample data has 30 periods, slow window is 26. First MACD value at index `window_slow - 1`.
        macd_df = ti.calculate_macd(self.sample_ohlc_df, window_slow=window_slow, window_fast=window_fast)
        self.assertIsInstance(macd_df, pd.DataFrame)
        self.assertFalse(macd_df.empty)
        self.assertEqual(len(macd_df), len(self.sample_ohlc_df))
        self.assertListEqual(list(macd_df.columns), ['macd_line', 'signal_line', 'macd_histogram'])
        # MACD line should have NaNs for `window_slow - 1` periods
        self.assertTrue(macd_df['macd_line'].head(window_slow - 1).isnull().all())
        self.assertFalse(macd_df['macd_line'].tail(1).isnull().any()) # Last value of MACD line should be calculable

    def test_calculate_macd_insufficient_data(self):
        # window_slow is 26, data has 5 rows
        macd_df = ti.calculate_macd(self.short_ohlc_df, window_slow=26, window_fast=12)
        self.assertIsInstance(macd_df, pd.DataFrame)
        # self.assertTrue(macd_df.empty) # ta returns df with all NaNs
        self.assertTrue(macd_df.isnull().all().all(), "MACD with insufficient data should be all NaNs or empty")

    def test_calculate_macd_empty_df(self):
        macd_df = ti.calculate_macd(self.empty_ohlc_df)
        self.assertIsInstance(macd_df, pd.DataFrame)
        self.assertTrue(macd_df.empty)

    def test_calculate_macd_missing_close_column(self):
        df_no_close = self.sample_ohlc_df[['open', 'high', 'low']].copy()
        macd_df = ti.calculate_macd(df_no_close)
        self.assertIsInstance(macd_df, pd.DataFrame)
        self.assertTrue(macd_df.empty)

if __name__ == '__main__':
    unittest.main()
