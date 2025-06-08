# Configuration file for the Trading Bot

# API Keys
# Replace with your actual API keys and secrets
API_KEY = "YOUR_API_KEY"
API_SECRET = "YOUR_API_SECRET"

# Trading Parameters
TRADE_SYMBOL = "BTC/USD"
TRADE_AMOUNT = 0.01  # Example: 0.01 BTC

# Data Collection Parameters
DATA_INTERVAL = "1h"  # Example: 1-hour candles

# Other settings
LOG_LEVEL = "INFO"  # Example: DEBUG, INFO, WARNING, ERROR, CRITICAL

# Example for a different API
# OTHER_API_KEY = "OTHER_API_KEY_HERE"
# OTHER_API_URL = "https://api.example.com/v1"

# Coingecko API
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"

# News API (Placeholder - replace with a real one if used)
NEWS_API_KEY = "YOUR_NEWS_API_KEY"
NEWS_API_URL = "https://newsapi.org/v2" # Example for newsapi.org, adjust if using another

# It's recommended to use environment variables for sensitive data like API keys.
import os
# API_KEY = os.getenv("TRADING_API_KEY", "YOUR_API_KEY")
# API_SECRET = os.getenv("TRADING_API_SECRET", "YOUR_API_SECRET")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_FALLBACK") # Loads from .env or environment

# Exchange API Configuration (e.g., Binance)
EXCHANGE_API_KEY = os.getenv("EXCHANGE_API_KEY", "YOUR_EXCHANGE_API_KEY_FALLBACK")
EXCHANGE_API_SECRET = os.getenv("EXCHANGE_API_SECRET", "YOUR_EXCHANGE_API_SECRET_FALLBACK")
EXCHANGE_API_URL = "https://api.binance.com/api/v3" # Example for Binance
