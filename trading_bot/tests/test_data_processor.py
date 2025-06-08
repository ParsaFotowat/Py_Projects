import unittest
import pandas as pd # Added for type hinting and direct use in tests
from trading_bot.processing.data_processor import process_coin_data, ohlc_list_to_dataframe

class TestDataProcessor(unittest.TestCase):

    def test_process_coin_data_success(self):
        """Test successful processing of valid coin data."""
        input_data = [
            {"id": "bitcoin", "symbol": "BTC", "name": "Bitcoin", "current_price": 50000},
            {"id": "ethereum", "symbol": "ETH", "name": "Ethereum", "market_cap": 500e9},
            {"id": "cardano", "symbol": "ada", "name": "Cardano"}, # Symbol already lowercase
        ]
        expected_output = [
            {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin", "trading_pair_spot": "BTCUSDT"},
            {"id": "ethereum", "symbol": "eth", "name": "Ethereum", "trading_pair_spot": "ETHUSDT"},
            {"id": "cardano", "symbol": "ada", "name": "Cardano", "trading_pair_spot": "ADAUSDT"},
        ]
        result = process_coin_data(input_data)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), len(expected_output))
        for i, processed_coin in enumerate(result):
            self.assertEqual(processed_coin["id"], expected_output[i]["id"])
            self.assertEqual(processed_coin["symbol"], expected_output[i]["symbol"])
            self.assertEqual(processed_coin["name"], expected_output[i]["name"])
            self.assertIn("trading_pair_spot", processed_coin)
            self.assertEqual(processed_coin["trading_pair_spot"], expected_output[i]["trading_pair_spot"])

    def test_process_empty_list(self):
        """Test processing of an empty list."""
        result = process_coin_data([])
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_process_coin_data_missing_keys(self):
        """Test processing data where some coins have missing essential keys."""
        input_data = [
            {"id": "bitcoin", "symbol": "BTC", "name": "Bitcoin"},
            {"id": "ethereum", "name": "Ethereum"},  # Missing 'symbol'
            {"symbol": "ADA", "name": "Cardano"},    # Missing 'id'
            {"id": "polkadot", "symbol": "DOT"},     # Missing 'name'
            {"id": "validcoin", "symbol": "VC", "name": "Valid Coin"},
        ]
        # Only 'bitcoin' and 'validcoin' should be processed successfully
        expected_output_count = 2
        result = process_coin_data(input_data)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), expected_output_count)

        # Check that the valid coins are present and correctly processed
        valid_ids = ["bitcoin", "validcoin"]
        processed_ids = [coin["id"] for coin in result]
        for vid in valid_ids:
            self.assertIn(vid, processed_ids)

        for coin in result:
            self.assertIn("id", coin)
            self.assertIn("symbol", coin)
            self.assertIn("name", coin)
            self.assertIn("trading_pair_spot", coin)
            if coin["id"] == "bitcoin":
                self.assertEqual(coin["symbol"], "btc")
                self.assertEqual(coin["trading_pair_spot"], "BTCUSDT")
            elif coin["id"] == "validcoin":
                self.assertEqual(coin["symbol"], "vc")
                self.assertEqual(coin["trading_pair_spot"], "VCUSDT")


    def test_process_coin_data_symbol_case_and_type(self):
        """Test symbol is correctly lowercased and handled if not string."""
        input_data = [
            {"id": "coin1", "symbol": "MixedCase", "name": "Coin One"},
            {"id": "coin2", "symbol": 123, "name": "Coin Two"}, # Non-string symbol
        ]
        expected_output = [
            {"id": "coin1", "symbol": "mixedcase", "name": "Coin One", "trading_pair_spot": "MIXEDCASEUSDT"},
            {"id": "coin2", "symbol": "123", "name": "Coin Two", "trading_pair_spot": "123USDT"},
        ]
        result = process_coin_data(input_data)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), len(expected_output))
        self.assertEqual(result, expected_output)

    def test_process_coin_data_with_various_malformed_entries(self):
        """Test with None, empty dicts, or other unexpected entries in the list."""
        input_data = [
            {"id": "bitcoin", "symbol": "BTC", "name": "Bitcoin"},
            None, # Should be skipped
            {},   # Should be skipped (missing all essential keys)
            {"id": "ethereum", "symbol": "ETH", "name": "Ethereum"},
            {"id": "onlyid"}, # Should be skipped
        ]
        expected_output_count = 2 # bitcoin and ethereum
        result = process_coin_data(input_data)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), expected_output_count)
        processed_ids = [coin["id"] for coin in result]
        self.assertIn("bitcoin", processed_ids)
        self.assertIn("ethereum", processed_ids)

    # Tests for ohlc_list_to_dataframe
    def test_ohlc_list_to_dataframe_success(self):
        """Test successful conversion of OHLC list to DataFrame."""
        ohlc_list = [
            [1678886400000, 24000.0, 24500.0, 23800.0, 24200.0],
            [1678972800000, 24200.0, 25000.0, 24100.0, 24900.0],
        ]
        df = ohlc_list_to_dataframe(ohlc_list, "testcoin") # Use direct import
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty)
        self.assertEqual(len(df), 2)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df.index))
        self.assertEqual(list(df.columns), ['open', 'high', 'low', 'close'])
        self.assertEqual(df.iloc[0]['open'], 24000.0)

    def test_ohlc_list_to_dataframe_empty_input(self):
        """Test conversion with empty list input."""
        df = ohlc_list_to_dataframe([], "testcoin") # Use direct import
        self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue(df.empty)

    def test_ohlc_list_to_dataframe_invalid_format(self):
        """Test conversion with invalid list format (e.g., wrong number of elements)."""
        ohlc_list_invalid = [[1678886400000, 24000.0, 24500.0]] # Missing low, close
        df = ohlc_list_to_dataframe(ohlc_list_invalid, "testcoin") # Use direct import
        self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue(df.empty)

    def test_ohlc_list_to_dataframe_non_numeric_ohlc(self):
        """Test conversion with non-numeric OHLC values (should coerce to NaN and drop)."""
        ohlc_list = [
            [1678886400000, "24000.0", "24500.0", "23800.0", "24200.0"], # Strings that can be numbers
            [1678972800000, 24200.0, "bad_data", 24100.0, 24900.0], # One bad data point
            [1679059200000, 24900.0, 25200.0, 24700.0, 25100.0],
        ]
        df = ohlc_list_to_dataframe(ohlc_list, "testcoin") # Use direct import
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2) # The row with "bad_data" should be dropped
        self.assertTrue(pd.api.types.is_float_dtype(df['open'])) # Check types
        self.assertTrue(df.loc[pd.to_datetime(1678886400000, unit='ms'), 'open'] == 24000.0)


if __name__ == '__main__':
    # pandas is already imported at the top level of the module now
    unittest.main()
