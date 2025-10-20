from django.contrib import admin
from django.urls import path
from core.views import index, academy, calendar_view
from django.urls import include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('academy/', academy, name='academy'),
    path('analytics/', include('analytics.urls')),
    path('calendar/', calendar_view, name='calendar_view'),
]
