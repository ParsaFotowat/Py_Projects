import unittest
from unittest.mock import patch, MagicMock, call
import pandas as pd
import time # <--- Added import
from trading_bot.core import strategy # The module we are testing

# Sample data that would be returned by mocked functions
SAMPLE_TOP_COINS_RAW = [
    {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin", "current_price": 50000, "market_cap": 1e12},
    {"id": "ethereum", "symbol": "eth", "name": "Ethereum", "current_price": 4000, "market_cap": 5e11},
]
SAMPLE_PROCESSED_COINS = [
    {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin", "trading_pair_spot": "BTCUSDT"},
    {"id": "ethereum", "symbol": "eth", "name": "Ethereum", "trading_pair_spot": "ETHUSDT"},
]
SAMPLE_OHLC_LIST = [[1678886400000, 100, 110, 90, 105]] * 30 # 30 days of data
SAMPLE_OHLC_DF = pd.DataFrame(SAMPLE_OHLC_LIST, columns=['timestamp', 'open', 'high', 'low', 'close'])
SAMPLE_OHLC_DF['timestamp'] = pd.to_datetime(SAMPLE_OHLC_DF['timestamp'], unit='ms')
SAMPLE_OHLC_DF.set_index('timestamp', inplace=True)

SAMPLE_NEWS_ARTICLES = [
    {"title": "Bitcoin Surges", "content_snippet": "Bitcoin price is up.", "source": "News1", "url": "url1", "published_at": "date1"},
    {"title": "Ethereum Stable", "content_snippet": "Ethereum holds steady.", "source": "News2", "url": "url2", "published_at": "date2"},
]

class TestTradingStrategy(unittest.TestCase):

    @patch('trading_bot.core.strategy.exchange_api.get_funding_rates')
    @patch('trading_bot.core.strategy.exchange_api.get_open_interest')
    @patch('trading_bot.core.strategy.exchange_api.calculate_volatility')
    @patch('trading_bot.core.strategy.exchange_api.get_recent_trades')
    @patch('trading_bot.core.strategy.exchange_api.get_order_book')
    @patch('trading_bot.core.strategy.sentiment_analyzer.analyze_sentiment_gemini')
    @patch('trading_bot.core.strategy.ti.calculate_macd')
    @patch('trading_bot.core.strategy.ti.calculate_bollinger_bands')
    @patch('trading_bot.core.strategy.ti.calculate_rsi')
    @patch('trading_bot.core.strategy.ti.calculate_sma')
    @patch('trading_bot.core.strategy.news_api.get_crypto_news')
    @patch('trading_bot.core.strategy.data_processor.ohlc_list_to_dataframe')
    @patch('trading_bot.core.strategy.cg_api.get_historical_ohlc')
    @patch('trading_bot.core.strategy.data_processor.process_coin_data')
    @patch('trading_bot.core.strategy.cg_api.get_top_coins')
    def test_run_trading_strategy_successful_flow(
            self, mock_get_top_coins, mock_process_coin_data, mock_get_historical_ohlc,
            mock_ohlc_list_to_df, mock_get_crypto_news, mock_calc_sma, mock_calc_rsi,
            mock_calc_bb, mock_calc_macd, mock_analyze_sentiment,
            mock_get_order_book, mock_get_recent_trades, mock_calc_volatility,
            mock_get_open_interest, mock_get_funding_rates):

        # --- Configure Mocks ---
        mock_get_top_coins.return_value = SAMPLE_TOP_COINS_RAW
        mock_process_coin_data.return_value = SAMPLE_PROCESSED_COINS
        mock_get_historical_ohlc.return_value = SAMPLE_OHLC_LIST
        mock_ohlc_list_to_df.return_value = SAMPLE_OHLC_DF
        mock_get_crypto_news.return_value = SAMPLE_NEWS_ARTICLES

        # Exchange API Mocks
        mock_get_order_book.return_value = {"bids": [["60000", "1"]], "asks": [["60001", "1"]], "lastUpdateId": 123}
        mock_get_recent_trades.return_value = [{"price": "60000.50", "qty": "0.002", "time": int(time.time()*1000)}]
        mock_calc_volatility.return_value = 0.5
        mock_get_open_interest.return_value = {"openInterest": "1000", "symbol": "BTCUSDT"}
        mock_get_funding_rates.return_value = [{"fundingRate": "0.0001"}]

        mock_calc_sma.return_value = pd.Series([100.0] * len(SAMPLE_OHLC_DF), index=SAMPLE_OHLC_DF.index)
        mock_calc_rsi.return_value = pd.Series([50.0] * len(SAMPLE_OHLC_DF), index=SAMPLE_OHLC_DF.index)
        mock_bb_df = pd.DataFrame({
            'bb_upper': [110.0] * len(SAMPLE_OHLC_DF),
            'bb_middle': [100.0] * len(SAMPLE_OHLC_DF),
            'bb_lower': [90.0] * len(SAMPLE_OHLC_DF)
        }, index=SAMPLE_OHLC_DF.index)
        mock_calc_bb.return_value = mock_bb_df
        mock_macd_df = pd.DataFrame({
            'macd_line': [1.0] * len(SAMPLE_OHLC_DF),
            'signal_line': [0.5] * len(SAMPLE_OHLC_DF),
            'macd_histogram': [0.5] * len(SAMPLE_OHLC_DF)
        }, index=SAMPLE_OHLC_DF.index)
        mock_calc_macd.return_value = mock_macd_df

        # Simulate alternating sentiment for variety
        # 2 coins, 2 articles each = 4 calls
        # Make first coin clearly positive, second clearly negative for testing distinct outcomes
        mock_analyze_sentiment.side_effect = ['positive', 'positive', 'negative', 'negative']

        # --- Run Strategy ---
        results = strategy.run_trading_strategy(top_n_coins=2)

        # --- Assertions ---
        self.assertEqual(len(results), 2) # Processed 2 coins
        mock_get_top_coins.assert_called_once_with(limit=2)
        self.assertEqual(mock_get_historical_ohlc.call_count, 2)
        self.assertEqual(mock_get_crypto_news.call_count, 2)
        self.assertEqual(mock_analyze_sentiment.call_count, 4)
        self.assertEqual(mock_get_order_book.call_count, 2)
        self.assertEqual(mock_get_recent_trades.call_count, 2)
        self.assertEqual(mock_calc_volatility.call_count, 2)
        self.assertEqual(mock_get_open_interest.call_count, 2)
        self.assertEqual(mock_get_funding_rates.call_count, 2)


        # Check data for the first coin (Bitcoin)
        btc_result = results[0]
        self.assertEqual(btc_result['symbol'], 'BTC')
        self.assertEqual(btc_result['latest_price'], 105)
        self.assertEqual(btc_result['sma_20'], 100.0)
        self.assertEqual(btc_result['rsi_14'], 50.0)
        self.assertEqual(btc_result['bollinger_bands']['middle'], 100.0)
        self.assertEqual(btc_result['macd']['line'], 1.0)
        self.assertEqual(btc_result['aggregated_sentiment'], 'positive')
        self.assertEqual(btc_result['signal'], 'CONSIDER_BUY')
        self.assertIsNotNone(btc_result['order_book_summary'])
        self.assertEqual(btc_result['volatility'], 0.5)
        self.assertEqual(btc_result['open_interest'], "1000")
        self.assertEqual(btc_result['funding_rate'], "0.0001")


        # Check data for the second coin (Ethereum)
        eth_result = results[1]
        self.assertEqual(eth_result['symbol'], 'ETH')
        self.assertEqual(eth_result['aggregated_sentiment'], 'negative')
        self.assertEqual(eth_result['signal'], 'CONSIDER_BUY')
        self.assertIsNotNone(eth_result['order_book_summary']) # Check if new keys are present


    @patch('trading_bot.core.strategy.exchange_api.get_funding_rates') # Order matters for decorators
    @patch('trading_bot.core.strategy.exchange_api.get_open_interest')
    @patch('trading_bot.core.strategy.exchange_api.calculate_volatility')
    @patch('trading_bot.core.strategy.exchange_api.get_recent_trades')
    @patch('trading_bot.core.strategy.exchange_api.get_order_book')
    @patch('trading_bot.core.strategy.sentiment_analyzer.analyze_sentiment_gemini')
    @patch('trading_bot.core.strategy.news_api.get_crypto_news')
    @patch('trading_bot.core.strategy.data_processor.ohlc_list_to_dataframe')
    @patch('trading_bot.core.strategy.cg_api.get_historical_ohlc')
    @patch('trading_bot.core.strategy.data_processor.process_coin_data')
    @patch('trading_bot.core.strategy.cg_api.get_top_coins')
    def test_run_trading_strategy_api_failures(
            self, mock_get_top_coins, mock_process_coin_data, mock_get_historical_ohlc,
            mock_ohlc_list_to_df, mock_get_crypto_news, mock_analyze_sentiment,
            mock_get_order_book, mock_get_recent_trades, mock_calc_volatility,
            mock_get_open_interest, mock_get_funding_rates): # Add new mocks

        # Scenario 1: get_top_coins returns empty
        mock_get_top_coins.return_value = []
        mock_process_coin_data.return_value = [] # If top_coins is empty, processed will be too
        results = strategy.run_trading_strategy(top_n_coins=1)
        self.assertEqual(len(results), 0)
        mock_get_top_coins.assert_called_once_with(limit=1)
        mock_get_historical_ohlc.assert_not_called() # Should not proceed

        # Reset mocks for next scenario - create a helper or re-patch for clarity if many scenarios
        all_mocks = [
            mock_get_top_coins, mock_process_coin_data, mock_get_historical_ohlc,
            mock_ohlc_list_to_df, mock_get_crypto_news, mock_analyze_sentiment,
            mock_get_order_book, mock_get_recent_trades, mock_calc_volatility,
            mock_get_open_interest, mock_get_funding_rates
        ]
        for m in all_mocks: m.reset_mock()


        # Scenario 2: get_historical_ohlc returns empty for one coin
        mock_get_top_coins.return_value = SAMPLE_TOP_COINS_RAW[:1]
        mock_process_coin_data.return_value = SAMPLE_PROCESSED_COINS[:1]
        mock_get_historical_ohlc.return_value = []
        mock_ohlc_list_to_df.return_value = pd.DataFrame()

        # Ensure other mocks are set up even if not primary to this test scenario,
        # to avoid them returning None and causing downstream issues if called unexpectedly.
        mock_get_crypto_news.return_value = [] # Assume no news if OHLC fails this early
        mock_get_order_book.return_value = {} # Empty dict for failed exchange calls
        mock_get_recent_trades.return_value = []
        mock_calc_volatility.return_value = None
        mock_get_open_interest.return_value = {}
        mock_get_funding_rates.return_value = []


        results = strategy.run_trading_strategy(top_n_coins=1)
        self.assertEqual(len(results), 1)
        btc_result = results[0]
        self.assertEqual(btc_result['symbol'], 'BTC')
        self.assertIsNone(btc_result['latest_price'])
        self.assertIsNone(btc_result['sma_20'])
        mock_get_crypto_news.assert_not_called()  # Still not called due to OHLC fail and continue
        mock_get_order_book.assert_not_called() # Also not called


    @patch('trading_bot.core.strategy.sentiment_analyzer.analyze_sentiment_gemini')
    @patch('trading_bot.core.strategy.ti') # Mock the entire ti module
    @patch('trading_bot.core.strategy.news_api.get_crypto_news')
    @patch('trading_bot.core.strategy.data_processor.ohlc_list_to_dataframe')
    @patch('trading_bot.core.strategy.cg_api.get_historical_ohlc')
    @patch('trading_bot.core.strategy.data_processor.process_coin_data')
    @patch('trading_bot.core.strategy.cg_api.get_top_coins')
    def test_run_trading_strategy_no_news(
            self, mock_get_top_coins, mock_process_coin_data, mock_get_historical_ohlc,
            mock_ohlc_list_to_df, mock_get_crypto_news, mock_ti_module, mock_analyze_sentiment):

        mock_get_top_coins.return_value = SAMPLE_TOP_COINS_RAW[:1]
        mock_process_coin_data.return_value = SAMPLE_PROCESSED_COINS[:1]
        mock_get_historical_ohlc.return_value = SAMPLE_OHLC_LIST
        mock_ohlc_list_to_df.return_value = SAMPLE_OHLC_DF
        mock_get_crypto_news.return_value = [] # No news articles

        # Mock TI functions to return some valid data so strategy proceeds
        mock_ti_module.calculate_sma.return_value = pd.Series([100.0] * len(SAMPLE_OHLC_DF), index=SAMPLE_OHLC_DF.index)
        mock_ti_module.calculate_rsi.return_value = pd.Series([50.0] * len(SAMPLE_OHLC_DF), index=SAMPLE_OHLC_DF.index)
        mock_bb_df_no_news = pd.DataFrame({
            'bb_upper': [110.0] * len(SAMPLE_OHLC_DF),
            'bb_middle': [100.0] * len(SAMPLE_OHLC_DF),
            'bb_lower': [90.0] * len(SAMPLE_OHLC_DF)
        }, index=SAMPLE_OHLC_DF.index)
        mock_ti_module.calculate_bollinger_bands.return_value = mock_bb_df_no_news
        mock_macd_df_no_news = pd.DataFrame({
            'macd_line': [1.0] * len(SAMPLE_OHLC_DF),
            'signal_line': [0.5] * len(SAMPLE_OHLC_DF),
            'macd_histogram': [0.5] * len(SAMPLE_OHLC_DF)
        }, index=SAMPLE_OHLC_DF.index)
        mock_ti_module.calculate_macd.return_value = mock_macd_df_no_news


        results = strategy.run_trading_strategy(top_n_coins=1)
        self.assertEqual(len(results), 1)
        btc_result = results[0]
        self.assertEqual(btc_result['aggregated_sentiment'], 'neutral') # Default
        self.assertEqual(btc_result['sentiment_score'], 0)
        self.assertEqual(btc_result['news_articles_analyzed'], 0)
        mock_analyze_sentiment.assert_not_called()


    @patch('trading_bot.core.strategy.sentiment_analyzer.analyze_sentiment_gemini')
    @patch('trading_bot.core.strategy.ti')
    @patch('trading_bot.core.strategy.news_api.get_crypto_news')
    @patch('trading_bot.core.strategy.data_processor.ohlc_list_to_dataframe')
    @patch('trading_bot.core.strategy.cg_api.get_historical_ohlc')
    @patch('trading_bot.core.strategy.data_processor.process_coin_data')
    @patch('trading_bot.core.strategy.cg_api.get_top_coins')
    def test_run_trading_strategy_indicator_calculation_issues(
            self, mock_get_top_coins, mock_process_coin_data, mock_get_historical_ohlc,
            mock_ohlc_list_to_df, mock_get_crypto_news, mock_ti_module, mock_analyze_sentiment):

        mock_get_top_coins.return_value = SAMPLE_TOP_COINS_RAW[:1]
        mock_process_coin_data.return_value = SAMPLE_PROCESSED_COINS[:1]
        mock_get_historical_ohlc.return_value = SAMPLE_OHLC_LIST
        mock_ohlc_list_to_df.return_value = SAMPLE_OHLC_DF # Valid DF initially
        mock_get_crypto_news.return_value = [] # No news to simplify

        # Simulate indicator functions returning empty Series/DataFrames
        mock_ti_module.calculate_sma.return_value = pd.Series(dtype=float)
        mock_ti_module.calculate_rsi.return_value = pd.Series(dtype=float)
        mock_ti_module.calculate_bollinger_bands.return_value = pd.DataFrame()
        mock_ti_module.calculate_macd.return_value = pd.DataFrame()

        results = strategy.run_trading_strategy(top_n_coins=1)
        self.assertEqual(len(results), 1)
        btc_result = results[0]
        self.assertIsNone(btc_result['sma_20'])
        self.assertIsNone(btc_result['rsi_14'])
        self.assertIsNone(btc_result['bollinger_bands'])
        self.assertIsNone(btc_result['macd'])
        self.assertEqual(btc_result['signal'], 'HOLD') # Should default to HOLD if no indicators

if __name__ == '__main__':
    unittest.main()
