import unittest
from unittest.mock import patch, Mock
import requests # Import requests for exception types
from trading_bot.api import coingecko

class TestCoingeckoAPI(unittest.TestCase):

    @patch('trading_bot.api.coingecko.requests.get')
    def test_get_top_coins_success(self, mock_get):
        """
        Test successful retrieval of top coins.
        """
        mock_response_data = [
            {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin", "current_price": 50000, "market_cap": 1000000000000},
            {"id": "ethereum", "symbol": "eth", "name": "Ethereum", "current_price": 4000, "market_cap": 500000000000},
            {"id": "cardano", "symbol": "ada", "name": "Cardano", "current_price": 2, "market_cap": 60000000000},
        ]
        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None  # Simulate successful HTTP status
        mock_get.return_value = mock_response

        limit = 3
        result = coingecko.get_top_coins(limit=limit)

        # Check if the function returns a list
        self.assertIsInstance(result, list)

        # Check if the list has the correct number of coins
        self.assertEqual(len(result), limit)

        # Check if each coin dictionary contains the expected keys
        expected_keys = ["id", "symbol", "name", "current_price", "market_cap"]
        for coin in result:
            self.assertIsInstance(coin, dict)
            for key in expected_keys:
                self.assertIn(key, coin)
            # Check specific data for the first coin to ensure mapping is correct
            self.assertEqual(result[0]["id"], mock_response_data[0]["id"])

    @patch('trading_bot.api.coingecko.requests.get')
    def test_get_top_coins_api_error(self, mock_get):
        """
        Test handling of API errors (e.g., network issue, 500 status).
        """
        mock_get.side_effect = requests.exceptions.RequestException("Test API Error")

        result = coingecko.get_top_coins(limit=5)
        self.assertEqual(result, []) # Expect an empty list on error

    @patch('trading_bot.api.coingecko.requests.get')
    def test_get_top_coins_http_error_status(self, mock_get):
        """
        Test handling of HTTP error statuses (e.g., 404, 503).
        """
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Test HTTP Error")
        mock_get.return_value = mock_response

        result = coingecko.get_top_coins(limit=5)
        self.assertEqual(result, []) # Expect an empty list on error

    @patch('trading_bot.api.coingecko.requests.get')
    def test_get_top_coins_json_decode_error(self, mock_get):
        """
        Test handling of JSON decoding errors.
        """
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Test JSON Decode Error") # ValueError is base for JSONDecodeError
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = coingecko.get_top_coins(limit=5)
        self.assertEqual(result, []) # Expect an empty list on error


    def test_get_top_coins_no_api_url(self):
        """
        Test behavior when COINGECKO_API_URL is not set (or empty).
        """
        with patch('trading_bot.api.coingecko.COINGECKO_API_URL', ''):
            result = coingecko.get_top_coins(limit=5)
            self.assertEqual(result, [])

    # Tests for get_historical_ohlc
    @patch('trading_bot.api.coingecko.requests.get')
    def test_get_historical_ohlc_success(self, mock_get):
        """Test successful retrieval of historical OHLC data."""
        mock_ohlc_data = [
            [1678886400000, 24000, 24500, 23800, 24200],
            [1678972800000, 24200, 25000, 24100, 24900],
        ]
        mock_response = Mock()
        mock_response.json.return_value = mock_ohlc_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = coingecko.get_historical_ohlc(coin_id="bitcoin", days="1")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        for item in result:
            self.assertIsInstance(item, list)
            self.assertEqual(len(item), 5) # Timestamp, O, H, L, C
        self.assertEqual(result, mock_ohlc_data)
        mock_get.assert_called_once_with(
            f"{coingecko.COINGECKO_API_URL}/coins/bitcoin/ohlc",
            params={"vs_currency": "usd", "days": "1"},
            timeout=15
        )

    @patch('trading_bot.api.coingecko.requests.get')
    def test_get_historical_ohlc_different_days(self, mock_get):
        """Test successful retrieval with a different 'days' parameter."""
        mock_ohlc_data = [[1678886400000, 24000, 24500, 23800, 24200]] # Dummy data
        mock_response = Mock()
        mock_response.json.return_value = mock_ohlc_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = coingecko.get_historical_ohlc(coin_id="ethereum", vs_currency="eur", days="7")
        self.assertEqual(result, mock_ohlc_data)
        mock_get.assert_called_once_with(
            f"{coingecko.COINGECKO_API_URL}/coins/ethereum/ohlc",
            params={"vs_currency": "eur", "days": "7"},
            timeout=15
        )

    @patch('trading_bot.api.coingecko.requests.get')
    def test_get_historical_ohlc_invalid_coin_id_404(self, mock_get):
        """Test error handling for an invalid coin_id (404 error)."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "404 Client Error", response=Mock(status_code=404)
        )
        mock_get.return_value = mock_response

        result = coingecko.get_historical_ohlc(coin_id="invalid_coin_id")
        self.assertEqual(result, [])

    @patch('trading_bot.api.coingecko.requests.get')
    def test_get_historical_ohlc_api_request_error(self, mock_get):
        """Test error handling for general API request issues."""
        mock_get.side_effect = requests.exceptions.RequestException("Test network error")

        result = coingecko.get_historical_ohlc(coin_id="bitcoin")
        self.assertEqual(result, [])

    @patch('trading_bot.api.coingecko.requests.get')
    def test_get_historical_ohlc_json_decode_error(self, mock_get):
        """Test error handling for JSON decoding issues."""
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("JSON decode error")
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = coingecko.get_historical_ohlc(coin_id="bitcoin")
        self.assertEqual(result, [])

    def test_get_historical_ohlc_no_coin_id(self):
        """Test that providing no coin_id returns an empty list and prints error."""
        result = coingecko.get_historical_ohlc(coin_id="")
        self.assertEqual(result, [])

    @patch('trading_bot.api.coingecko.requests.get')
    def test_get_historical_ohlc_unexpected_data_format(self, mock_get):
        """Test handling of unexpected data format from API."""
        mock_response = Mock()
        mock_response.json.return_value = {"unexpected": "data"} # Not a list of lists
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = coingecko.get_historical_ohlc(coin_id="bitcoin")
        self.assertEqual(result, [])

        mock_response.json.return_value = [[1,2,3],[4,5,6]] # list of lists, but inner list not len 5
        result = coingecko.get_historical_ohlc(coin_id="bitcoin")
        self.assertEqual(result, [])


if __name__ == '__main__':
    # This allows running the tests directly from this file
    # However, it's better to use 'python -m unittest discover' from the root directory
    unittest.main()
