import requests
from .. import config  # Use relative import to access config

COINGECKO_API_URL = config.COINGECKO_API_URL

def get_top_coins(limit: int = 5) -> list[dict]:
    """
    Fetches the top N cryptocurrencies by market cap from the Coingecko API.

    Args:
        limit: The number of top coins to fetch. Defaults to 5.

    Returns:
        A list of dictionaries, where each dictionary contains information
        about a coin (e.g., id, symbol, name, current_price, market_cap).
        Returns an empty list if an error occurs.
    """
    if not COINGECKO_API_URL:
        print("Error: Coingecko API URL not configured.")
        return []

    endpoint = "/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": limit,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "false"  # Not requesting price change percentage
    }

    try:
        response = requests.get(f"{COINGECKO_API_URL}{endpoint}", params=params, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)

        coins_data = response.json()

        # Extract relevant information
        top_coins = []
        for coin in coins_data:
            top_coins.append({
                "id": coin.get("id"),
                "symbol": coin.get("symbol"),
                "name": coin.get("name"),
                "current_price": coin.get("current_price"),
                "market_cap": coin.get("market_cap")
            })
        return top_coins

    except requests.exceptions.RequestException as e:
        print(f"Error fetching top coins from Coingecko API: {e}")
        return []
    except ValueError as e: # Includes JSONDecodeError
        print(f"Error decoding JSON response for top coins from Coingecko API: {e}")
        return []

def get_historical_ohlc(coin_id: str, vs_currency: str = 'usd', days: str = 'max') -> list[list]:
    """
    Fetches historical OHLC (Open, High, Low, Close) data for a specific coin from Coingecko.

    Args:
        coin_id: The ID of the coin (e.g., "bitcoin").
        vs_currency: The target currency (e.g., "usd"). Defaults to 'usd'.
        days: Data duration (e.g., 1, 7, 30, "max"). Defaults to 'max'.

    Returns:
        A list of lists, where each inner list is [timestamp, open, high, low, close].
        Returns an empty list if an error occurs or data is not found.
    """
    if not COINGECKO_API_URL:
        print("Error: Coingecko API URL not configured.")
        return []
    if not coin_id:
        print("Error: Coin ID must be provided for historical data.")
        return []

    endpoint = f"/coins/{coin_id}/ohlc"
    params = {
        "vs_currency": vs_currency,
        "days": days,
    }

    try:
        response = requests.get(f"{COINGECKO_API_URL}{endpoint}", params=params, timeout=15) # Longer timeout for potentially larger data
        response.raise_for_status()  # Raises HTTPError for bad responses (4XX or 5XX)

        ohlc_data = response.json()

        # Expected format: [[timestamp, open, high, low, close], ...]
        if not isinstance(ohlc_data, list) or not all(isinstance(item, list) and len(item) == 5 for item in ohlc_data):
            print(f"Error: Unexpected data format received for OHLC data for {coin_id}.")
            # print(f"Received data: {ohlc_data[:2]}...") # Uncomment for debugging if needed
            return []

        return ohlc_data

    except requests.exceptions.HTTPError as e:
        # Specifically handle 404 for coin not found
        if e.response.status_code == 404:
            print(f"Error: Coin '{coin_id}' not found or no OHLC data available for the specified parameters on Coingecko.")
        else:
            print(f"HTTP error fetching OHLC data for {coin_id} from Coingecko: {e}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Request error fetching OHLC data for {coin_id} from Coingecko: {e}")
        return []
    except ValueError as e:  # Includes JSONDecodeError
        print(f"Error decoding JSON response for OHLC data for {coin_id} from Coingecko: {e}")
        return []

if __name__ == '__main__':
    # Example usage:
    # Example usage for get_top_coins:
    # ... (previous example code for get_top_coins can remain here or be removed if too verbose) ...
    print("Fetching top 3 coins...")
    top_coins_example = get_top_coins(limit=3)
    if top_coins_example:
        for c in top_coins_example:
            print(f"Coin: {c['name']}, Price: {c['current_price']}")
            # Fetch historical data for the first coin found
            if c.get('id'):
                print(f"Fetching historical (1 day) OHLC for {c['name']} ({c['id']})...")
                historical_data = get_historical_ohlc(coin_id=c['id'], days='1')
                if historical_data:
                    print(f"Found {len(historical_data)} data points for the last day.")
                    # print(f"Last data point: {historical_data[-1]}") # Shows [timestamp, o, h, l, c]
                else:
                    print(f"No historical data found for {c['name']}.")
                break # Just do it for the first coin in this example
    else:
        print("Could not retrieve top coins for example.")

    print("\nFetching historical OHLC for Bitcoin (7 days)...")
    btc_ohlc = get_historical_ohlc(coin_id="bitcoin", days="7")
    if btc_ohlc:
        print(f"Found {len(btc_ohlc)} data points for Bitcoin (7 days).")
        # print(f"First data point: {btc_ohlc[0]}")
        # print(f"Last data point: {btc_ohlc[-1]}")
    else:
        print("Could not retrieve Bitcoin OHLC data.")

    print("\nFetching historical OHLC for a non-existent coin...")
    invalid_ohlc = get_historical_ohlc(coin_id="not_a_real_coin_id_123")
    # Expected: Error message and empty list
    print(f"Result for non-existent coin: {invalid_ohlc}")
