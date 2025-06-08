# API Modules
from trading_bot.api import coingecko as cg_api
from trading_bot.api import news as news_api
from trading_bot.api import exchange as exchange_api # New import

# Processing Modules
from trading_bot.processing import data_processor

# Analysis Modules
from trading_bot.analysis import technical_indicators as ti
from trading_bot.analysis import sentiment_analyzer

# Utilities
import pandas as pd

# Configuration - though API keys are handled within their respective modules
# from trading_bot import config

def run_trading_strategy(top_n_coins: int = 3):
    """
    Runs the core trading strategy logic.

    Args:
        top_n_coins: The number of top coins to process.

    Returns:
        A list of dictionaries, where each dictionary contains the coin info,
        latest indicators, aggregated sentiment, latest price, and a placeholder signal.
    """
    print(f"Running trading strategy for top {top_n_coins} coins...")
    strategy_results = []

    # 1. Fetch Top Coins
    top_coins_raw = cg_api.get_top_coins(limit=top_n_coins)
    if not top_coins_raw:
        print("No top coins data received. Exiting strategy.")
        return strategy_results

    processed_coins = data_processor.process_coin_data(top_coins_raw)
    if not processed_coins:
        print("No coins left after initial processing. Exiting strategy.")
        return strategy_results

    # 2. Iterate Through Coins
    for coin in processed_coins:
        coin_id = coin.get("id")
        coin_symbol = coin.get("symbol", "N/A").upper()
        coin_name = coin.get("name", "Unknown Coin")
        print(f"\nProcessing data for {coin_name} ({coin_symbol})...")

        # Consolidated data for this coin
        coin_decision_data = {
            "coin_id": coin_id,
            "symbol": coin_symbol,
            "name": coin_name,
            "latest_price": None,
            "sma_20": None,
            "rsi_14": None,
            "bollinger_bands": None, # Could be {'upper': val, 'middle': val, 'lower': val}
            "macd": None, # Could be {'line': val, 'signal': val, 'hist': val}
            "aggregated_sentiment": "neutral", # Default
            "sentiment_score": 0, # Example: -1 for negative, 0 for neutral, 1 for positive
            "news_articles_analyzed": 0,
            "order_book_summary": None, # Placeholder for bid/ask spread, depth, etc.
            "volatility": None,
            "open_interest": None,
            "funding_rate": None,
            "decision_factors": [], # List of strings explaining decision
            "signal": "HOLD" # Default signal
        }

        # 3. Gather Data
        # Fetch historical OHLC
        ohlc_data_list = cg_api.get_historical_ohlc(coin_id=coin_id, days="90") # Fetch enough data for indicators
        if not ohlc_data_list:
            print(f"Could not fetch OHLC data for {coin_name}. Skipping further analysis for this coin.")
            strategy_results.append(coin_decision_data) # Append with default/None values
            continue

        ohlc_df = data_processor.ohlc_list_to_dataframe(ohlc_data_list, coin_id=coin_id)
        if ohlc_df.empty:
            print(f"OHLC data for {coin_name} is empty after DataFrame conversion. Skipping.")
            strategy_results.append(coin_decision_data)
            continue

        if 'close' in ohlc_df.columns and not ohlc_df['close'].empty:
            coin_decision_data["latest_price"] = ohlc_df['close'].iloc[-1]
        else:
            print(f"No 'close' price data available in OHLC for {coin_name}.")
            # Potentially skip coin if latest price is crucial and missing
            # For now, we'll allow it to proceed and have None for indicators

        # Fetch news articles
        # Using coin_name as keyword, could also use symbol or combine
        news_articles = news_api.get_crypto_news(keywords=coin_name, limit=5)

        # Fetch Exchange-Specific Data (using trading_pair_spot from processed_coins)
        trading_pair = coin.get("trading_pair_spot", f"{coin_symbol}USDT") # Default if not processed

        order_book_data = exchange_api.get_order_book(symbol=trading_pair)
        if order_book_data and "error" not in order_book_data:
            # Simple summary: e.g. mid-price, or just a note that it's available
            if order_book_data.get("bids") and order_book_data.get("asks"):
                try:
                    best_bid = float(order_book_data["bids"][0][0])
                    best_ask = float(order_book_data["asks"][0][0])
                    coin_decision_data["order_book_summary"] = {
                        "best_bid": best_bid,
                        "best_ask": best_ask,
                        "spread": best_ask - best_bid if best_bid and best_ask else None
                    }
                except (ValueError, IndexError, TypeError):
                    coin_decision_data["order_book_summary"] = "Error processing order book"


        recent_trades_list = exchange_api.get_recent_trades(symbol=trading_pair, limit=200) # Need enough for volatility window
        if recent_trades_list and isinstance(recent_trades_list, list) and (not recent_trades_list[0] or "error" not in recent_trades_list[0]):
            coin_decision_data["volatility"] = exchange_api.calculate_volatility(recent_trades_list, window_seconds=300) # 5-min volatility

        # Open Interest and Funding Rates (relevant for futures, using base symbol for now)
        # These might use a different symbol format (e.g. BTCUSD_PERP vs BTCUSDT spot)
        # For placeholder stage, we'll use the spot trading_pair or coin_symbol.
        # In a real system, this would need careful handling of symbol mapping.
        oi_data = exchange_api.get_open_interest(symbol=trading_pair)
        if oi_data and "error" not in oi_data:
            coin_decision_data["open_interest"] = oi_data.get("openInterest")

        funding_data_list = exchange_api.get_funding_rates(symbol=trading_pair)
        if funding_data_list and isinstance(funding_data_list, list) and (not funding_data_list[0] or "error" not in funding_data_list[0]):
             # Assuming the first entry is the most relevant/latest
            coin_decision_data["funding_rate"] = funding_data_list[0].get("fundingRate")


        # 4. Analyze Data
        # Calculate Technical Indicators
        if not ohlc_df.empty and 'close' in ohlc_df.columns:
            sma_20 = ti.calculate_sma(ohlc_df, window=20)
            if sma_20 is not None and not sma_20.empty:
                coin_decision_data["sma_20"] = sma_20.iloc[-1] if not pd.isna(sma_20.iloc[-1]) else None

            rsi_14 = ti.calculate_rsi(ohlc_df, window=14)
            if rsi_14 is not None and not rsi_14.empty:
                coin_decision_data["rsi_14"] = rsi_14.iloc[-1] if not pd.isna(rsi_14.iloc[-1]) else None

            bbands = ti.calculate_bollinger_bands(ohlc_df, window=20)
            if bbands is not None and not bbands.empty:
                coin_decision_data["bollinger_bands"] = {
                    "upper": bbands['bb_upper'].iloc[-1] if not pd.isna(bbands['bb_upper'].iloc[-1]) else None,
                    "middle": bbands['bb_middle'].iloc[-1] if not pd.isna(bbands['bb_middle'].iloc[-1]) else None,
                    "lower": bbands['bb_lower'].iloc[-1] if not pd.isna(bbands['bb_lower'].iloc[-1]) else None,
                }

            macd = ti.calculate_macd(ohlc_df) # Using default windows
            if macd is not None and not macd.empty:
                 coin_decision_data["macd"] = {
                    "line": macd['macd_line'].iloc[-1] if not pd.isna(macd['macd_line'].iloc[-1]) else None,
                    "signal": macd['signal_line'].iloc[-1] if not pd.isna(macd['signal_line'].iloc[-1]) else None,
                    "histogram": macd['macd_histogram'].iloc[-1] if not pd.isna(macd['macd_histogram'].iloc[-1]) else None,
                }
        else:
            print(f"Skipping technical indicator calculation for {coin_name} due to lack of OHLC data.")

        # Analyze Sentiment
        sentiments = []
        if news_articles:
            coin_decision_data["news_articles_analyzed"] = len(news_articles)
            for article in news_articles:
                # Use a snippet or title for sentiment analysis to save tokens/time
                text_to_analyze = article.get("title", "") + " " + article.get("content_snippet", "")
                if text_to_analyze.strip():
                    sentiment = sentiment_analyzer.analyze_sentiment_gemini(text_to_analyze.strip())
                    if sentiment: # analyze_sentiment_gemini can return None
                        sentiments.append(sentiment)

        if sentiments:
            # Aggregate sentiment (simple example: mode or count-based)
            positive_count = sentiments.count('positive')
            negative_count = sentiments.count('negative')
            # neutral_count = sentiments.count('neutral') # Not always used in score

            if positive_count > negative_count:
                coin_decision_data["aggregated_sentiment"] = "positive"
                coin_decision_data["sentiment_score"] = 1
            elif negative_count > positive_count:
                coin_decision_data["aggregated_sentiment"] = "negative"
                coin_decision_data["sentiment_score"] = -1
            # else, it remains 'neutral' with score 0

        # 5. Placeholder for Gemini Pro Decision / Simple Rule-Based Logic
        # This is where a more sophisticated model or complex rules would go.
        # For now, simple rules:
        if coin_decision_data["rsi_14"] is not None and coin_decision_data["rsi_14"] < 30:
            coin_decision_data["decision_factors"].append("RSI < 30 (Oversold)")
            if coin_decision_data["aggregated_sentiment"] == "positive":
                coin_decision_data["signal"] = "BUY"
                coin_decision_data["decision_factors"].append("Positive sentiment supports BUY")
            elif coin_decision_data["aggregated_sentiment"] == "negative":
                coin_decision_data["signal"] = "HOLD" # Oversold but negative news
                coin_decision_data["decision_factors"].append("Negative sentiment suggests caution despite oversold RSI")
            else: # Neutral sentiment
                coin_decision_data["signal"] = "CONSIDER_BUY"
                coin_decision_data["decision_factors"].append("Neutral sentiment, RSI oversold")


        elif coin_decision_data["rsi_14"] is not None and coin_decision_data["rsi_14"] > 70:
            coin_decision_data["decision_factors"].append("RSI > 70 (Overbought)")
            if coin_decision_data["aggregated_sentiment"] == "negative":
                coin_decision_data["signal"] = "SELL"
                coin_decision_data["decision_factors"].append("Negative sentiment supports SELL")
            elif coin_decision_data["aggregated_sentiment"] == "positive":
                coin_decision_data["signal"] = "HOLD" # Overbought but positive news
                coin_decision_data["decision_factors"].append("Positive sentiment suggests caution despite overbought RSI")
            else: # Neutral sentiment
                coin_decision_data["signal"] = "CONSIDER_SELL"
                coin_decision_data["decision_factors"].append("Neutral sentiment, RSI overbought")

        if coin_decision_data["macd"] is not None and coin_decision_data["macd"]["line"] is not None and coin_decision_data["macd"]["signal"] is not None:
            if coin_decision_data["macd"]["line"] > coin_decision_data["macd"]["signal"] and \
               (len(coin_decision_data["decision_factors"]) == 0 or "RSI" not in " ".join(coin_decision_data["decision_factors"])): # Avoid conflicting RSI signals
                coin_decision_data["decision_factors"].append("MACD line crossed above signal line")
                if coin_decision_data["signal"] == "HOLD": coin_decision_data["signal"] = "CONSIDER_BUY" # Upgrade HOLD
            elif coin_decision_data["macd"]["line"] < coin_decision_data["macd"]["signal"] and \
                 (len(coin_decision_data["decision_factors"]) == 0 or "RSI" not in " ".join(coin_decision_data["decision_factors"])):
                coin_decision_data["decision_factors"].append("MACD line crossed below signal line")
                if coin_decision_data["signal"] == "HOLD": coin_decision_data["signal"] = "CONSIDER_SELL" # Upgrade HOLD

        if not coin_decision_data["decision_factors"]:
            coin_decision_data["decision_factors"].append("No strong technical or sentiment signals.")

        strategy_results.append(coin_decision_data)
        print(f"Finished processing for {coin_name}. Signal: {coin_decision_data['signal']}")

    return strategy_results

if __name__ == '__main__':
    # This allows running the strategy directly for testing,
    # but ensure API keys are available if not mocked.
    # For GEMINI_API_KEY, it needs to be set in the environment or .env file.

    # Example: Load .env if running this file directly and you have a .env file
    # This is typically done in the main entry point of an application.
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("Attempted to load .env file.")
    except ImportError:
        print(".env file not loaded (dotenv library not found or not used here). Ensure env vars are set if real APIs are hit.")

    results = run_trading_strategy(top_n_coins=2)
    print("\n--- Strategy Results ---")
    for result in results:
        print(f"\nCoin: {result['name']} ({result['symbol']})")
        print(f"  Latest Price: {result['latest_price']}")
        print(f"  SMA (20): {_format_value(result.get('sma_20'))}")
        print(f"  RSI (14): {_format_value(result.get('rsi_14'))}")
        # print(f"  Bollinger Bands: {result.get('bollinger_bands', 'N/A')}")
        # print(f"  MACD: {result.get('macd', 'N/A')}")
        print(f"  Aggregated Sentiment: {result.get('aggregated_sentiment','N/A')} (Score: {result.get('sentiment_score','N/A')}, Articles: {result.get('news_articles_analyzed',0)})")
        print(f"  Volatility (5min): {_format_value(result.get('volatility'), precision=5)}")
        print(f"  Order Book Spread: {_format_value(result.get('order_book_summary', {}).get('spread'), precision=4)}")
        print(f"  Open Interest: {_format_value(result.get('open_interest'))}")
        print(f"  Funding Rate: {_format_value(result.get('funding_rate'), precision=4)}")
        print(f"  Decision Factors: {', '.join(result.get('decision_factors', ['N/A']))}")
        print(f"  Signal: {result.get('signal', 'N/A')}")

def _format_value(value, precision: int = 2, default_na: str = "N/A"):
    """Helper to format numeric values or return N/A for main print."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return default_na
    if isinstance(value, float):
        return f"{value:.{precision}f}"
    return str(value)
