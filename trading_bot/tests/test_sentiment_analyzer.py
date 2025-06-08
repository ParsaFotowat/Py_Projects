import unittest
from unittest.mock import patch, MagicMock
from trading_bot.analysis import sentiment_analyzer
from google.api_core import exceptions as google_exceptions # For mocking Google API errors

# Since sentiment_analyzer imports config, we might need to patch config values
# if they are read at module level and affect test behavior.
# GEMINI_API_KEY = config.GEMINI_API_KEY is at module level in sentiment_analyzer.py

class TestSentimentAnalyzer(unittest.TestCase):

    def setUp(self):
        # Reset any module-level state if necessary, e.g., if API key was changed by a test
        # For this structure, we'll patch 'sentiment_analyzer.GEMINI_API_KEY' or 'sentiment_analyzer.genai'
        pass

    @patch('trading_bot.analysis.sentiment_analyzer.genai')
    def test_positive_sentiment(self, mock_genai):
        # Configure the mock Gemini model and its response
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "positive"
        mock_response.parts = [MagicMock()] # Ensure response.parts is not empty
        mock_response.prompt_feedback = None
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        # Patch the API key to ensure the function proceeds
        with patch('trading_bot.analysis.sentiment_analyzer.GEMINI_API_KEY', 'fake_valid_key'):
            sentiment = sentiment_analyzer.analyze_sentiment_gemini("This is a great news!")
            self.assertEqual(sentiment, "positive")
            mock_genai.configure.assert_called_with(api_key='fake_valid_key')
            mock_model.generate_content.assert_called_once()

    @patch('trading_bot.analysis.sentiment_analyzer.genai')
    def test_negative_sentiment(self, mock_genai):
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "negative"
        mock_response.parts = [MagicMock()]
        mock_response.prompt_feedback = None
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        with patch('trading_bot.analysis.sentiment_analyzer.GEMINI_API_KEY', 'fake_valid_key'):
            sentiment = sentiment_analyzer.analyze_sentiment_gemini("This is bad news.")
            self.assertEqual(sentiment, "negative")

    @patch('trading_bot.analysis.sentiment_analyzer.genai')
    def test_neutral_sentiment(self, mock_genai):
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "neutral"
        mock_response.parts = [MagicMock()]
        mock_response.prompt_feedback = None
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        with patch('trading_bot.analysis.sentiment_analyzer.GEMINI_API_KEY', 'fake_valid_key'):
            sentiment = sentiment_analyzer.analyze_sentiment_gemini("This is some news.")
            self.assertEqual(sentiment, "neutral")

    @patch('trading_bot.analysis.sentiment_analyzer.genai')
    def test_api_error_google_exception(self, mock_genai):
        mock_model = MagicMock()
        # Simulate a Google API error (e.g., permission denied, server error)
        mock_model.generate_content.side_effect = google_exceptions.PermissionDenied("API key invalid")
        mock_genai.GenerativeModel.return_value = mock_model

        with patch('trading_bot.analysis.sentiment_analyzer.GEMINI_API_KEY', 'fake_key_causes_error'):
            sentiment = sentiment_analyzer.analyze_sentiment_gemini("Text doesn't matter here.")
            self.assertEqual(sentiment, "neutral") # Default fallback

    @patch('trading_bot.analysis.sentiment_analyzer.genai')
    def test_api_error_other_exception(self, mock_genai):
        mock_model = MagicMock()
        # Simulate a generic exception during API call
        mock_model.generate_content.side_effect = Exception("Unexpected error")
        mock_genai.GenerativeModel.return_value = mock_model

        with patch('trading_bot.analysis.sentiment_analyzer.GEMINI_API_KEY', 'fake_valid_key'):
            sentiment = sentiment_analyzer.analyze_sentiment_gemini("Some text.")
            self.assertEqual(sentiment, "neutral")

    def test_empty_input_text(self):
        with patch('trading_bot.analysis.sentiment_analyzer.GEMINI_API_KEY', 'fake_valid_key'):
            sentiment = sentiment_analyzer.analyze_sentiment_gemini("")
            self.assertEqual(sentiment, "neutral")
            sentiment_none = sentiment_analyzer.analyze_sentiment_gemini(None)
            self.assertEqual(sentiment_none, "neutral")
            sentiment_whitespace = sentiment_analyzer.analyze_sentiment_gemini("   ")
            self.assertEqual(sentiment_whitespace, "neutral")

    @patch('trading_bot.analysis.sentiment_analyzer.genai')
    def test_unexpected_response_text(self, mock_genai):
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "confused" # Not one of 'positive', 'negative', 'neutral'
        mock_response.parts = [MagicMock()]
        mock_response.prompt_feedback = None
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        with patch('trading_bot.analysis.sentiment_analyzer.GEMINI_API_KEY', 'fake_valid_key'):
            sentiment = sentiment_analyzer.analyze_sentiment_gemini("This is confusing news.")
            self.assertEqual(sentiment, "neutral") # Should default

    @patch('trading_bot.analysis.sentiment_analyzer.genai')
    def test_response_blocked(self, mock_genai):
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.parts = [] # No parts
        mock_response.prompt_feedback = MagicMock()
        mock_response.prompt_feedback.block_reason = "SAFETY"
        # Also test if .text access raises ValueError (as per code)
        type(mock_response).text = unittest.mock.PropertyMock(side_effect=ValueError("Blocked"))

        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        with patch('trading_bot.analysis.sentiment_analyzer.GEMINI_API_KEY', 'fake_valid_key'):
            sentiment = sentiment_analyzer.analyze_sentiment_gemini("This content might be blocked.")
            self.assertEqual(sentiment, "neutral")

    def test_no_api_key_configured_at_all(self):
        # Patch the API_KEY at the module level of sentiment_analyzer
        with patch('trading_bot.analysis.sentiment_analyzer.GEMINI_API_KEY', None):
            sentiment = sentiment_analyzer.analyze_sentiment_gemini("Text here.")
            self.assertIsNone(sentiment) # Or 'neutral' depending on chosen behavior in function

    def test_api_key_is_placeholder(self):
        with patch('trading_bot.analysis.sentiment_analyzer.GEMINI_API_KEY', "YOUR_GEMINI_API_KEY_FALLBACK"):
            sentiment = sentiment_analyzer.analyze_sentiment_gemini("Text here.")
            self.assertIsNone(sentiment) # Or 'neutral'

if __name__ == '__main__':
    unittest.main()
