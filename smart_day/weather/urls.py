from django.urls import path
from . import views

app_name = 'weather'

urlpatterns = [
    path('current/', views.current_weather_view, name='current'),
    path('forecast/', views.weather_forecast_view, name='forecast'),
    
    # Переносим их сюда:
    path('about/', views.about_view, name='about'),
    path('contacts/', views.contacts_view, name='contacts'),
    path('privacy/', views.privacy_view, name='privacy'),
]