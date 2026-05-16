from django.shortcuts import render

def current_weather_view(request):
    # Пример запроса
    # response = requests.get('URL_API_ПОГОДЫ').json()
    context = {
        'temp': 18, # Данные из ответа API
        'city': 'Пермь'
    }
    return render(request, 'weather/current.html', context)

def weather_forecast_view(request):
    return render(request, 'weather/forecast.html')