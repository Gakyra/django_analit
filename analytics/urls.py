from django.urls import path
from .views import analytics_form, analytics_result, analytics_loading

urlpatterns = [
    path('form/', analytics_form, name='analytics_form'),
    path('result/', analytics_result, name='analytics_result'),
    path("loading/", analytics_loading, name="analytics_loading"),
]
