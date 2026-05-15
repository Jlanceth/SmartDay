from django.urls import path
from . import views

app_name = 'weather'

urlpatterns = [
    path('current/', views.current_weather_view, name='current'),

    path('forecast/', views.weather_forecast_view, name='forecast'),
]