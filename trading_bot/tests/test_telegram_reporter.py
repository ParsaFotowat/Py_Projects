import unittest
from trading_bot.reporting.telegram_reporter import format_telegram_report, _format_value

class TestTelegramReporter(unittest.TestCase):

    sample_coin_full_data = {
        "coin_id": "bitcoin", "symbol": "BTC", "name": "Bitcoin",
        "latest_price": 45123.4567,
        "sma_20": 44000.123,
        "rsi_14": 55.678,
        "bollinger_bands": {"upper": 46000.0, "middle": 44000.123, "lower": 42000.0},
        "macd": {"line": 150.56, "signal": 140.32, "histogram": 10.24},
        "aggregated_sentiment": "positive",
        "sentiment_score": 1,
        "news_articles_analyzed": 3,
        "decision_factors": ["RSI neutral", "MACD bullish crossover"],
        "signal": "CONSIDER_BUY"
    }

    sample_coin_missing_data = {
        "coin_id": "ethereum", "symbol": "ETH", "name": "Ethereum",
        "latest_price": None, # Missing
        "sma_20": None,
        "rsi_14": 25.0,
        "bollinger_bands": None, # Missing
        "macd": {"line": None, "signal": None, "histogram": None}, # All parts None
        "aggregated_sentiment": "neutral",
        "sentiment_score": 0,
        "news_articles_analyzed": 0, # No news
        "decision_factors": ["RSI < 30 (Oversold)"],
        "signal": "HOLD"
    }

    def test_format_value_helper(self):
        self.assertEqual(_format_value(123.4567, precision=2), "123.46")
        self.assertEqual(_format_value(123.0, precision=2), "123.00")
        self.assertEqual(_format_value(None), "N/A")
        self.assertEqual(_format_value(float('nan')), "N/A")
        self.assertEqual(_format_value("text"), "text")
        self.assertEqual(_format_value(10, precision=0), "10")


    def test_format_telegram_report_single_coin_full_data(self):
        report = format_telegram_report([self.sample_coin_full_data])

        self.assertIn("<b>Trading Report</b>", report)
        self.assertIn("<b>1. Bitcoin (BTC)</b>", report)
        self.assertIn("Action: CONSIDER_BUY", report)
        self.assertIn("Entry Price: 45123.46", report) # Check formatting
        self.assertIn("Stop Loss: N/A", report)
        self.assertIn("Take Profit: N/A", report)

        self.assertIn("Primary Price Action Signals: RSI (14) at 55.68, BB Middle (SMA 20) at 44000.12", report)
        self.assertIn("Lagging Indicator Confirmation: MACD Line: 150.56, Signal: 140.32, Hist: 10.24", report)
        self.assertIn("Sentiment & Macro Analysis: Aggregated news sentiment: positive (Score: 1, Articles: 3)", report)
        self.assertIn("Key Decision Factors: RSI neutral, MACD bullish crossover", report)

        # Check for placeholder sections
        self.assertIn("<b>Long-term:</b>\n    Action: N/A", report)
        self.assertIn("<b>Leveraged Recommendations:</b>", report)
        self.assertIn("<b>Short-term:</b>\n    Position: N/A", report) # For leveraged

        # Check for bolding and line breaks
        # Expected <b> tags: 1 for "Trading Report" + 7 for a single coin's sections
        self.assertEqual(report.count("<b>"), 8)
        self.assertEqual(report.count("</b>"), report.count("<b>"))
        self.assertTrue(report.count("\n") >= 20) # Rough estimate of line breaks, this seems fine

    def test_format_telegram_report_single_coin_missing_data(self):
        report = format_telegram_report([self.sample_coin_missing_data])

        self.assertIn("<b>1. Ethereum (ETH)</b>", report)
        self.assertIn("Action: HOLD", report)
        self.assertIn("Entry Price: N/A", report) # Missing data

        self.assertIn("Primary Price Action Signals: RSI (14) at 25.00", report) # Only RSI available
        # BB Middle would be N/A if bbands or bbands['middle'] is None, so it won't appear unless explicitly N/A
        self.assertNotIn("BB Middle", report)

        self.assertIn("Lagging Indicator Confirmation: N/A", report) # MACD parts are None
        self.assertIn("Sentiment & Macro Analysis: Aggregated news sentiment: neutral (Score: 0, Articles: 0)", report)
        self.assertIn("Key Decision Factors: RSI < 30 (Oversold)", report)

    def test_format_telegram_report_multiple_coins(self):
        report = format_telegram_report([self.sample_coin_full_data, self.sample_coin_missing_data])
        self.assertIn("<b>1. Bitcoin (BTC)</b>", report)
        self.assertIn("<b>2. Ethereum (ETH)</b>", report)
        self.assertTrue(report.find("<b>2. Ethereum (ETH)</b>") > report.find("<b>1. Bitcoin (BTC)</b>"))

    def test_format_telegram_report_empty_input(self):
        report = format_telegram_report([])
        self.assertEqual(report, "<b>Trading Report</b>\n\nNo data to report.")

if __name__ == '__main__':
    unittest.main()
