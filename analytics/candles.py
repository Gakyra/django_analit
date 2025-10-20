from django.shortcuts import render
from .coingecko import get_supported_assets

BINANCE_SYMBOLS = {
    "bitcoin": "btcusdt",
    "ethereum": "ethusdt",
    "solana": "solusdt",
    "avalanche-2": "avaxusdt",
    "dogecoin": "dogeusdt",
}

def candles_view(request):
    asset_id = request.GET.get("asset", "bitcoin")
    interval = request.GET.get("interval", "1m")
    assets = get_supported_assets()
    asset_name = assets.get(asset_id, asset_id.upper())
    binance_symbol = BINANCE_SYMBOLS.get(asset_id, "btcusdt")
    timeframes = ["1m", "5m", "15m", "30m", "1h", "3h", "6h", "1d"]

    return render(request, "candles.html", {
        "asset_id": asset_id,
        "interval": interval,
        "assets": assets,
        "asset_name": asset_name,
        "binance_symbol": binance_symbol,
        "timeframes": timeframes
    })
