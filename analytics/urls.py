from django.urls import path
from .views import analytics_form, analytics_result
from .candles import candles_view

urlpatterns = [
    path('view/', analytics_form, name='analytics_form'),
    path('result/', analytics_result, name='analytics_result'),
    path('candles/', candles_view, name='candles_view'),
]
