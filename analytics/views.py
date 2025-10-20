from django.shortcuts import render, redirect
from django.core.cache import cache
from django.http import JsonResponse
import time
import random

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

last_request_time = 0

# 📈 Головна сторінка з порадою дня
def index(request):
    tips = [
        "Інвестуй регулярно, а не емоційно.",
        "Краще пропустити можливість, ніж втратити капітал.",
        "Диверсифікація — твій щит від ризиків.",
        "Не купуй актив, якого не розумієш.",
        "Інвестування — це марафон, а не спринт.",
        "Не реагуй на кожну новину — май стратегію.",
        "Ризик — це не ворог, а інструмент. Керуй ним.",
        "Почни з малого, але почни сьогодні.",
        "Твій найбільший актив — це час.",
        "Не шукай ідеальний момент — шукай дисципліну.",
        "Фінансова грамотність — основа будь-якого портфеля.",
        "Інвестуй у себе — знання приносять найвищий дохід.",
        "Пам’ятай: ринок завжди має фази. Не панікуй.",
        "Завжди май резервний фонд — це твоя безпека.",
        "Вивчай історію ринку — вона повторюється.",
    ]
    tip = random.choice(tips)
    return render(request, "index.html", {"tip": tip})

# 📊 Форма вибору активу
def analytics_form(request):
    assets = get_supported_assets()
    return render(request, "analytics_form.html", {"assets": assets})

# ⏳ Прелоадинг даних
def analytics_loading(request):
    asset_id = request.GET.get("asset_id", "bitcoin")
    period = request.GET.get("period", "30")
    forecast = request.GET.get("forecast", "off")
    prefix = f"{asset_id}_{period}"

    preload_success = preload_single_asset_sync(asset_id, period)
    if preload_success:
        return JsonResponse({"status": "ready"})
    else:
        return JsonResponse({"status": "error", "message": f"Аналіз для {asset_id} недоступний. Спробуйте пізніше."})

# 📉 Результати аналітики
def analytics_result(request):
    if request.method == "POST":
        asset_id = request.POST.get("asset_id", "bitcoin")
        period = request.POST.get("period", "30")
        forecast_enabled = request.POST.get("forecast") == "on"
        return redirect(f"/analytics/result/?asset_id={asset_id}&period={period}&forecast={'on' if forecast_enabled else 'off'}")

    asset_id = request.GET.get("asset_id", "bitcoin")
    period = request.GET.get("period", "30")
    forecast_enabled = request.GET.get("forecast") == "on"
    prefix = f"{asset_id}_{period}"

    chart = cache.get(f"chart_{prefix}")
    volume = cache.get(f"volume_{prefix}")
    asset = cache.get(f"asset_{prefix}")

    if not chart or not volume or not asset:
        return render(request, "loading.html", {
            "asset_id": asset_id,
            "period": period,
            "forecast": "on" if forecast_enabled else "off"
        })

    volatility = calculate_volatility(chart)
    risk_level = estimate_risk(asset.get("change", 0), volatility)
    sentiment = estimate_sentiment(asset.get("volume", 0), asset.get("change", 0))
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

# 🚀 Прелоадинг кешу
def preload_single_asset_sync(asset_id, period):
    global last_request_time
    prefix = f"{asset_id}_{period}"
    now = time.time()

    if now - last_request_time < 30:
        print(f"[PRELOAD] ⏳ Пропущено {prefix} — слишком рано ({round(now - last_request_time)} сек)")
        return False
    last_request_time = now

    print(f"[PRELOAD] Старт загрузки {prefix}")
    t0 = time.time()

    chart = get_chart_data(asset_id, days=period)
    volume = get_volume_data(asset_id, days=period)
    asset = get_asset_data(asset_id)

    print(f"[PRELOAD] {prefix} → chart={len(chart)}, volume={len(volume)}, price={asset.get('price')}")

    if len(chart) >= 2 and len(volume) >= 2 and asset.get("price", 0) > 0:
        cache.set(f"chart_{prefix}", chart, timeout=3600)
        cache.set(f"volume_{prefix}", volume, timeout=3600)
        cache.set(f"asset_{prefix}", asset, timeout=3600)
        print(f"[PRELOAD] ✅ Кешировано {prefix}")
        print(f"[TIME] preload завершён за {round((time.time() - t0)*1000)} ms")
        return True
    else:
        print(f"[PRELOAD] ⚠️ Пропущено {prefix} — данные невалидны")
        return False
