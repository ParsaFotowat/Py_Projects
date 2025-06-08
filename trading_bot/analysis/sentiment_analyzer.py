import google.generativeai as genai
from google.api_core import exceptions as google_exceptions # For specific Google API errors
import requests.exceptions # For potential network errors if genai uses requests internally, or for general handling
from trading_bot import config

# Configure Gemini API Key at the module level when it's first imported,
# or ensure it's configured before making an API call.
# However, it's often better to configure it right before use or ensure config is loaded.
GEMINI_API_KEY = config.GEMINI_API_KEY
MODEL_NAME = 'gemini-pro' # Or other suitable models like 'gemini-1.5-flash-latest'

def analyze_sentiment_gemini(text_content: str) -> str | None:
    """
    Analyzes the sentiment of the given text content using Google's Gemini API.

    Args:
        text_content: The text to analyze.

    Returns:
        A string 'positive', 'negative', or 'neutral' representing the sentiment.
        Returns 'neutral' as a default/fallback in case of errors or if sentiment
        cannot be reliably determined, or None if API key is missing.
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_FALLBACK":
        print("Error: Gemini API Key not configured or is using placeholder.")
        return None # Or 'neutral' if a default is preferred even without key

    if not text_content or not isinstance(text_content, str) or not text_content.strip():
        # print("Warning: Empty or invalid text content provided for sentiment analysis.")
        return 'neutral' # Default for empty text

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(MODEL_NAME)

        prompt = (
            "Analyze the sentiment of the following news article text. "
            "Return only one word: 'positive', 'negative', or 'neutral'. "
            f"Text: \"{text_content}\""
        )

        # It's good practice to limit the size of the text content if it can be very long
        # to avoid excessive API costs or hitting token limits.
        # For example: text_content = text_content[:5000] # Limit to first 5000 chars

        response = model.generate_content(prompt)

        if response.parts:
            # .text can sometimes raise exceptions if the response is blocked etc.
            try:
                sentiment = response.text.strip().lower()
                if sentiment in ['positive', 'negative', 'neutral']:
                    return sentiment
                else:
                    print(f"Warning: Gemini returned unexpected sentiment: '{sentiment}'. Defaulting to neutral.")
                    return 'neutral'
            except ValueError as ve: # If response.text is not accessible due to blocking
                print(f"Error accessing response text from Gemini (possibly blocked content): {ve}")
                if response.prompt_feedback and response.prompt_feedback.block_reason:
                    print(f"Prompt feedback: Blocked due to {response.prompt_feedback.block_reason}")
                return 'neutral'

        elif response.prompt_feedback and response.prompt_feedback.block_reason:
             print(f"Warning: Content generation blocked by Gemini. Reason: {response.prompt_feedback.block_reason}. Defaulting to neutral.")
             return 'neutral'
        else:
            print("Warning: Gemini returned no usable content. Defaulting to neutral.")
            return 'neutral'

    except google_exceptions.GoogleAPIError as e:
        # This can include various API errors like InvalidArgument, PermissionDenied (bad API key), etc.
        print(f"Error: Gemini API error: {e}")
        return 'neutral'
    except requests.exceptions.RequestException as e: # If genai uses requests and has a network issue
        print(f"Error: Network error during Gemini API call: {e}")
        return 'neutral'
    except Exception as e:
        # Catch-all for other unexpected errors (e.g., issues with genai library itself)
        print(f"An unexpected error occurred during sentiment analysis: {e}")
        return 'neutral'

if __name__ == '__main__':
    # --- IMPORTANT ---
    # To run this example, you MUST have a valid GEMINI_API_KEY.
    # You can set it as an environment variable:
    # export GEMINI_API_KEY="your_actual_api_key_here"
    # Or, create a .env file in the root of this project with:
    # GEMINI_API_KEY="your_actual_api_key_here"
    # Make sure python-dotenv is installed (it is in requirements.txt)
    # and that the .env file is loaded (usually done automatically if main.py uses dotenv.load_dotenv())
    # For this direct script run, ensure config.GEMINI_API_KEY is loaded correctly.

    # If config.py is in trading_bot/ and this script is trading_bot/analysis/sentiment_analyzer.py
    # and you run `python -m trading_bot.analysis.sentiment_analyzer` from the root,
    # then `from trading_bot import config` should work.
    # If you run `python trading_bot/analysis/sentiment_analyzer.py` directly from root,
    # Python's module system might get confused about relative imports.

    print(f"Attempting to use Gemini API Key: {GEMINI_API_KEY[:10]}... (if configured)")

    sample_positive_text = "Bitcoin price surged today after positive regulatory news. Investors are very optimistic."
    sample_negative_text = "Major exchange hacked, leading to significant losses and fear in the crypto market."
    sample_neutral_text = "The cryptocurrency market cap remained relatively stable over the weekend. Trading volume was average."
    empty_text = ""

    print(f"\nAnalyzing positive text: '{sample_positive_text}'")
    sentiment_p = analyze_sentiment_gemini(sample_positive_text)
    print(f"Sentiment: {sentiment_p}")

    print(f"\nAnalyzing negative text: '{sample_negative_text}'")
    sentiment_n = analyze_sentiment_gemini(sample_negative_text)
    print(f"Sentiment: {sentiment_n}")

    print(f"\nAnalyzing neutral text: '{sample_neutral_text}'")
    sentiment_u = analyze_sentiment_gemini(sample_neutral_text)
    print(f"Sentiment: {sentiment_u}")

    print(f"\nAnalyzing empty text: '{empty_text}'")
    sentiment_e = analyze_sentiment_gemini(empty_text)
    print(f"Sentiment (empty): {sentiment_e}")

    # Test with a very long text (first 100 chars) to see if it works,
    # but be mindful of real API usage limits.
    long_text = "This is a very long text designed to test the API's ability to handle extensive input. " * 50
    # print(f"\nAnalyzing long text (first 100 chars): '{long_text[:100]}...'")
    # sentiment_l = analyze_sentiment_gemini(long_text)
    # print(f"Sentiment (long text): {sentiment_l}")

    # Example of how it might be called if key is missing or placeholder
    original_key = GEMINI_API_KEY
    GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_FALLBACK" # Simulate missing/placeholder key
    print("\nSimulating missing API key:")
    sentiment_no_key = analyze_sentiment_gemini("This text won't be analyzed.")
    print(f"Sentiment (no key): {sentiment_no_key}")
    GEMINI_API_KEY = original_key # Restore key if it was valid for other tests

    # Example of how it might be called if key is invalid (will be caught by mock in tests)
    # GEMINI_API_KEY = "invalid_key_for_testing_live_api_error"
    # print("\nSimulating invalid API key (LIVE TEST - MIGHT FAIL OR COST $ IF KEY IS VALID):")
    # sentiment_invalid_key = analyze_sentiment_gemini("Testing invalid key.")
    # print(f"Sentiment (invalid key): {sentiment_invalid_key}")
    # GEMINI_API_KEY = original_key
