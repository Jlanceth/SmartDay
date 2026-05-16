import requests
from django.shortcuts import render

WEATHER_API_KEY = '9fe4e13a07ddd935d3aa98e8ee5a85b9'
CITY_ID = '511196'  # Пермь


def current_weather_view(request):
    """Отображение текущей детальной погоды"""
    url = f"https://api.openweathermap.org/data/2.5/weather?id={CITY_ID}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            context = {
                'temp': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'condition': data['weather'][0]['description'].capitalize(),
                'icon': data['weather'][0]['icon'],  # Код иконки погоды (например, "01d")
                'humidity': data['main']['humidity'],  # Влажность в %
                'wind_speed': data['wind']['speed'],  # Скорость ветра в м/с
                'pressure': round(data['main']['pressure'] * 0.750064),  # Переводим гПа в мм рт. ст.
                'city': 'Пермь',
                'error': False
            }
        else:
            context = {'error': True, 'city': 'Пермь'}
    except requests.RequestException:
        context = {'error': True, 'city': 'Пермь'}
        
    return render(request, 'weather/current.html', context)


def weather_forecast_view(request):
    """Отображение прогноза погоды (каждые 3 часа на ближайшие дни)"""
    url = f"https://api.openweathermap.org/data/2.5/forecast?id={CITY_ID}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    forecast_list = []
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            # API возвращает список из 40 элементов (каждые 3 часа на 5 дней).
            # Возьмем, например, первые 8 элементов (прогноз на ближайшие 24 часа), как график на сайте.
            for item in data['list'][:8]:
                forecast_list.append({
                    'datetime': item['dt_txt'],  # Строка даты/времени от API
                    'temp': round(item['main']['temp']),
                    'condition': item['weather'][0]['description'].capitalize(),
                    'icon': item['weather'][0]['icon'],
                    'humidity': item['main']['humidity'],
                })
            context = {
                'forecast': forecast_list,
                'city': 'Пермь',
                'error': False
            }
        else:
            context = {'error': True, 'city': 'Пермь'}
    except requests.RequestException:
        context = {'error': True, 'city': 'Пермь'}
        
    return render(request, 'weather/forecast.html', context)