from django.shortcuts import render
from .coingecko import (
    get_supported_assets,
    get_asset_data,
    get_chart_data,
    get_volume_data,
    calculate_volatility,
    estimate_risk,
    estimate_sentiment,
    generate_forecast
)

def preload_assets(request):
    assets = get_supported_assets()
    periods = ["1", "7", "30", "90"]

    for asset_id in assets:
        for period in periods:
            chart = get_chart_data(asset_id, days=period)
            volume = get_volume_data(asset_id, days=period)
            asset = get_asset_data(asset_id)

            cache_prefix = f"{asset_id}_{period}"
            chart_key = f"chart_{cache_prefix}"
            volume_key = f"volume_{cache_prefix}"
            asset_key = f"asset_{cache_prefix}"

            if len(chart) >= 2 and len(volume) >= 2 and asset.get("price", 0) > 0:
                request.session[chart_key] = chart
                request.session[volume_key] = volume
                request.session[asset_key] = asset

def analytics_form(request):
    preload_assets(request)
    assets = get_supported_assets()
    return render(request, "analytics_form.html", {"assets": assets})

def analytics_result(request):
    if request.method != "POST":
        return render(request, "analytics_form.html", {"assets": get_supported_assets()})

    asset_id = request.POST.get("asset_id", "bitcoin")
    period = request.POST.get("period", "30")
    forecast_enabled = request.POST.get("forecast") == "on"

    cache_prefix = f"{asset_id}_{period}"
    chart_key = f"chart_{cache_prefix}"
    volume_key = f"volume_{cache_prefix}"
    asset_key = f"asset_{cache_prefix}"

    chart = get_chart_data(asset_id, days=period)
    volume = get_volume_data(asset_id, days=period)
    asset = get_asset_data(asset_id)

    chart_ok = len(chart) >= 2
    volume_ok = len(volume) >= 2
    asset_ok = isinstance(asset, dict) and asset.get("price", 0) > 0 and asset.get("market_cap", 0) > 0

    if chart_ok and volume_ok and asset_ok:
        request.session[chart_key] = chart
        request.session[volume_key] = volume
        request.session[asset_key] = asset
    else:
        chart = request.session.get(chart_key, [[0, 1]])
        volume = request.session.get(volume_key, [[0, 1]])
        asset = request.session.get(asset_key, {
            "name": asset_id,
            "symbol": asset_id.upper(),
            "price": 1,
            "change": 0,
            "market_cap": 1,
            "volume": 1,
        })

    volatility = calculate_volatility(chart)
    risk_level = estimate_risk(asset["change"], volatility)
    sentiment = estimate_sentiment(asset["volume"], asset["change"])
    forecast = generate_forecast(chart) if forecast_enabled else None

    return render(request, "analytics_result.html", {
        "asset_id": asset_id,
        "asset": asset,
        "period": period,
        "chart": chart,
        "volume": volume,
        "volatility": volatility,
        "risk_level": risk_level,
        "sentiment": sentiment,
        "forecast": forecast
    })