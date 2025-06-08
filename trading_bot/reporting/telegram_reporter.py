from typing import List, Dict, Any
import pandas as pd # For pd.isna checks, though data should be primitive by now

def _format_value(value, precision: int = 2, default_na: str = "N/A"):
    """Helper to format numeric values or return N/A."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return default_na
    if isinstance(value, float):
        return f"{value:.{precision}f}"
    return str(value)

def format_telegram_report(decision_data_list: List[Dict[str, Any]]) -> str:
    """
    Formats the decision data for multiple coins into a single Telegram report string.

    Args:
        decision_data_list: A list of coin_decision_data dictionaries.

    Returns:
        A single string formatted for Telegram with HTML-like tags.
    """
    if not decision_data_list:
        return "<b>Trading Report</b>\n\nNo data to report."

    full_report_parts = ["<b>Trading Report</b>\n"]

    for i, data in enumerate(decision_data_list):
        coin_name = data.get('name', 'Unknown Coin')
        coin_symbol = data.get('symbol', 'N/A').upper()

        report_part = f"\n<b>{i+1}. {coin_name} ({coin_symbol})</b>\n"

        # --- Spot Recommendations ---
        report_part += "<b>Spot Recommendations:</b>\n"
        # Short-term Spot
        report_part += "  <b>Short-term:</b>\n"
        report_part += f"    Action: {_format_value(data.get('signal', 'N/A'))}\n"
        report_part += f"    Entry Price: {_format_value(data.get('latest_price'))}\n"
        report_part += f"    Stop Loss: N/A\n"  # Placeholder
        report_part += f"    Take Profit: N/A\n" # Placeholder
        report_part += "    Rationale:\n"

        # Rationale - Primary Price Action Signals
        primary_signals = []
        rsi_14 = data.get('rsi_14')
        if rsi_14 is not None and not pd.isna(rsi_14):
            primary_signals.append(f"RSI (14) at {_format_value(rsi_14)}")

        bbands = data.get('bollinger_bands')
        if bbands and isinstance(bbands, dict):
            bb_middle = bbands.get('middle')
            # Could add more BB related signals here if logic existed
            if bb_middle is not None and not pd.isna(bb_middle):
                 primary_signals.append(f"BB Middle (SMA 20) at {_format_value(bb_middle)}")

        if not primary_signals:
            primary_signals.append("N/A")
        report_part += f"      Primary Price Action Signals: {', '.join(primary_signals)}\n"

        # Rationale - Lagging Indicator Confirmation
        lagging_signals = []
        macd = data.get('macd')
        if macd and isinstance(macd, dict):
            macd_line = macd.get('line')
            signal_line = macd.get('signal')
            hist = macd.get('histogram')
            macd_parts = []
            if macd_line is not None and not pd.isna(macd_line): macd_parts.append(f"MACD Line: {_format_value(macd_line)}")
            if signal_line is not None and not pd.isna(signal_line): macd_parts.append(f"Signal: {_format_value(signal_line)}")
            if hist is not None and not pd.isna(hist): macd_parts.append(f"Hist: {_format_value(hist)}")
            if macd_parts: lagging_signals.append(', '.join(macd_parts))

        sma_20 = data.get('sma_20') # This was also BB Middle
        # if sma_20 is not None and not pd.isna(sma_20) and not any("SMA 20" in s for s in primary_signals): # Avoid duplicate if BB middle used
        #     lagging_signals.append(f"SMA (20) at {_format_value(sma_20)}")

        if not lagging_signals:
            lagging_signals.append("N/A")
        report_part += f"      Lagging Indicator Confirmation: {', '.join(lagging_signals)}\n"

        # Rationale - Sentiment & Macro Analysis
        agg_sentiment = _format_value(data.get('aggregated_sentiment', 'N/A'))
        sentiment_score = _format_value(data.get('sentiment_score', 'N/A'), precision=0)
        articles_analyzed = _format_value(data.get('news_articles_analyzed', 0), precision=0)
        report_part += f"      Sentiment & Macro Analysis: Aggregated news sentiment: {agg_sentiment} (Score: {sentiment_score}, Articles: {articles_analyzed})\n"

        # Decision Factors from strategy
        decision_factors = data.get('decision_factors', [])
        if decision_factors:
             report_part += f"      Key Decision Factors: {', '.join(decision_factors)}\n"


        # Long-term Spot (Placeholder)
        report_part += "  <b>Long-term:</b>\n"
        report_part += "    Action: N/A\n"
        report_part += "    Entry Price: N/A\n"
        report_part += "    Stop Loss: N/A\n"
        report_part += "    Take Profit: N/A\n"
        report_part += "    Rationale: N/A\n"

        # --- Leveraged Recommendations (Placeholders) ---
        report_part += "<b>Leveraged Recommendations:</b>\n"
        report_part += "  <b>Short-term:</b>\n"
        report_part += "    Position: N/A\n"
        report_part += "    Leverage: N/A\n"
        report_part += "    Entry Price: N/A\n"
        report_part += "    Stop Loss: N/A\n"
        report_part += "    Take Profit: N/A\n"
        report_part += "    Rationale: N/A\n"
        report_part += "  <b>Long-term:</b>\n"
        report_part += "    Position: N/A\n"
        report_part += "    Leverage: N/A\n"
        report_part += "    Entry Price: N/A\n"
        report_part += "    Stop Loss: N/A\n"
        report_part += "    Take Profit: N/A\n"
        report_part += "    Rationale: N/A\n"

        full_report_parts.append(report_part)

    return "\n".join(full_report_parts)


if __name__ == '__main__':
    # Sample data for direct testing
    sample_decision_data = [
        {
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
        },
        {
            "coin_id": "ethereum", "symbol": "ETH", "name": "Ethereum",
            "latest_price": 3000.0,
            "sma_20": None, # Missing data example
            "rsi_14": 25.0, # Oversold
            "bollinger_bands": None,
            "macd": None,
            "aggregated_sentiment": "negative",
            "sentiment_score": -1,
            "news_articles_analyzed": 1,
            "decision_factors": ["RSI < 30 (Oversold)", "Negative sentiment suggests caution despite oversold RSI"],
            "signal": "HOLD"
        },
        {
            "coin_id": "cardano", "symbol": "ADA", "name": "Cardano",
            "latest_price": 1.5,
            "sma_20": 1.45,
            "rsi_14": 75.0, # Overbought
            "bollinger_bands": {"upper": 1.6, "middle": 1.45, "lower": 1.3},
            "macd": {"line": -0.05, "signal": -0.04, "histogram": -0.01}, # Bearish
            "aggregated_sentiment": "neutral",
            "sentiment_score": 0,
            "news_articles_analyzed": 0, # No news
            "decision_factors": ["RSI > 70 (Overbought)", "Neutral sentiment, RSI overbought"],
            "signal": "CONSIDER_SELL"
        }
    ]

    report = format_telegram_report(sample_decision_data)
    print(report)

    print("\n--- Empty Report Test ---")
    empty_report = format_telegram_report([])
    print(empty_report)
