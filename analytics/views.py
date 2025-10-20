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

def analytics_form(request):
    assets = get_supported_assets()
    return render(request, "analytics_form.html", {"assets": assets})

def analytics_result(request):
    asset_id = request.POST.get("asset_id")
    period = request.POST.get("period", "30")
    forecast_enabled = request.POST.get("forecast") == "on"

    asset = get_asset_data(asset_id)
    chart = get_chart_data(asset_id, days=period)
    volume = get_volume_data(asset_id, days=period)

    if not chart or not isinstance(chart, list):
        chart = [[0, asset["price"]]]
    if not volume or not isinstance(volume, list):
        volume = [[0, asset["volume"]]]

    volatility = calculate_volatility(chart)
    risk_level = estimate_risk(asset["change"], volatility)
    sentiment = estimate_sentiment(asset["volume"], asset["change"])
    forecast = generate_forecast(chart) if forecast_enabled else None

    return render(request, "analytics_result.html", {
        "asset": asset,
        "chart": chart,
        "volume": volume,
        "volatility": volatility,
        "risk_level": risk_level,
        "sentiment": sentiment,
        "forecast": forecast,
        "period": period,
        "asset_id": asset_id,
    })
