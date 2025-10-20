import requests
import statistics

BASE_URL = "https://api.coingecko.com/api/v3"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/117.0 Safari/537.36"
}

def get_supported_assets():
    return {
        "bitcoin": "Bitcoin",
        "ethereum": "Ethereum",
        "solana": "Solana",
        "avalanche-2": "Avalanche",
        "dogecoin": "Dogecoin",
    }


def get_asset_data(asset_id):
    try:
        response = requests.get(
            f"{BASE_URL}/coins/{asset_id}",
            params={"localization": "false"},
            headers=HEADERS,
            timeout=5
        )
        print(f"[RAW] asset_data[{asset_id}] → {response.text[:300]}")
        data = response.json()
        return {
            "name": data.get("name", asset_id),
            "symbol": data.get("symbol", asset_id.upper()),
            "price": data.get("market_data", {}).get("current_price", {}).get("usd", 0),
            "change": data.get("market_data", {}).get("price_change_percentage_24h", 0),
            "market_cap": data.get("market_data", {}).get("market_cap", {}).get("usd", 0),
            "volume": data.get("market_data", {}).get("total_volume", {}).get("usd", 0),
        }
    except Exception as e:
        print(f"[EXCEPTION] asset_data[{asset_id}] → {e}")
        return {
            "name": asset_id,
            "symbol": asset_id.upper(),
            "price": 0,
            "change": 0,
            "market_cap": 0,
            "volume": 0,
        }

def get_chart_data(asset_id, days="30"):
    try:
        response = requests.get(
            f"{BASE_URL}/coins/{asset_id}/market_chart",
            params={"vs_currency": "usd", "days": days},
            headers=HEADERS,
            timeout=5
        )
        print(f"[RAW] chart_data[{asset_id}_{days}] → {response.text[:300]}")
        data = response.json()
        return [p for p in data.get("prices", []) if isinstance(p, list) and len(p) == 2]
    except Exception as e:
        print(f"[EXCEPTION] chart_data[{asset_id}_{days}] → {e}")
        return []

def get_volume_data(asset_id, days="30"):
    try:
        response = requests.get(
            f"{BASE_URL}/coins/{asset_id}/market_chart",
            params={"vs_currency": "usd", "days": days},
            headers=HEADERS,
            timeout=5
        )
        print(f"[RAW] volume_data[{asset_id}_{days}] → {response.text[:300]}")
        data = response.json()
        return [v for v in data.get("total_volumes", []) if isinstance(v, list) and len(v) == 2]
    except Exception as e:
        print(f"[EXCEPTION] volume_data[{asset_id}_{days}] → {e}")
        return []

def calculate_volatility(chart):
    prices = [point[1] for point in chart if isinstance(point, list) and len(point) == 2]
    return round(statistics.stdev(prices), 2) if len(prices) >= 2 else 0

def estimate_risk(change, volatility):
    if volatility > 50:
        return "Високий"
    elif volatility > 20:
        return "Середній"
    else:
        return "Низький"

def estimate_sentiment(volume, change):
    if change > 5 and volume > 1_000_000_000:
        return "Оптимістичний"
    elif change < -5:
        return "Негативний"
    else:
        return "Нейтральний"

def generate_forecast(chart):
    try:
        if len(chart) < 2:
            return None
        last_price = chart[-1][1]
        trend = chart[-1][1] - chart[-2][1]
        return {
            "direction": "⬆️" if trend > 0 else "⬇️",
            "target": round(last_price + trend * 3, 2)
        }
    except Exception as e:
        print(f"[EXCEPTION] forecast → {e}")
        return None
