import requests
from django.shortcuts import render
from recommendations.views import get_geomagnetic_data, get_pollen_data

WEATHER_API_KEY = '9fe4e13a07ddd935d3aa98e8ee5a85b9'
CITY_ID = '511196'  # Пермь


def current_weather_view(request):
    """Отображение текущей детальной погоды со всеми экологическими индексами"""
    
    # 1. Запрашиваем базовые данные погоды из OpenWeatherMap
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?id={CITY_ID}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    
    # Инициализируем базовый контекст на случай ошибки погоды
    context = {'error': False, 'city': 'Пермь'}
    
    try:
        response = requests.get(weather_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Рассчитываем УФ на основе облачности, как в твоем get_weather_data
            clouds = data.get('clouds', {}).get('all', 0)
            dynamic_uv = 1 if clouds > 80 else (3 if clouds > 40 else 5)
            
            context.update({
                'temp': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'condition': data['weather'][0]['description'].capitalize(),
                'icon': data['weather'][0]['icon'],
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed'],
                'pressure': round(data['main']['pressure'] * 0.750064),
                'uv_index': dynamic_uv,  # ОБЯЗАТЕЛЬНО ПЕРЕДАЕМ СЮДА УФ-ИНДЕКС
            })
        else:
            context['error'] = True
            context['uv_index'] = 1  # Заглушка при ошибке погоды
    except requests.RequestException:
        context['error'] = True
        context['uv_index'] = 1

    # 2. Подтягиваем геомагнитные данные (Kp-индекс)
    geo_data = get_geomagnetic_data()
    context['kp_index'] = geo_data.get('kp_index', 2) # ПЕРЕДАЕМ РЕАЛЬНЫЙ КП-ИНДЕКС ДЛЯ ШАБЛОНА

    # 3. Подтягиваем данные по пыльце
    weather_for_pollen = {
        'temp': context.get('temp', 20),
        'wind_speed': context.get('wind_speed', 2),
        'rain': 0
    }

    pollen_data = get_pollen_data(weather_for_pollen)

    context['allergen_level'] = pollen_data.get('allergen_level', 'Низкий')
    context['birch_value'] = pollen_data.get('birch_value', 0)

    # 4. Рендерим страницу с ПОЛНЫМ набором данных
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


def about_view(request):
    """Отображение страницы О проекте"""
    return render(request, 'pages/about.html')

def contacts_view(request):
    """Отображение страницы Контакты"""
    return render(request, 'pages/contacts.html')

def privacy_view(request):
    """Отображение страницы Политика конфиденциальности"""
    return render(request, 'pages/privacy.html')