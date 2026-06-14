from datetime import date
from tasks_calendar.models import Tasks
# Импортируй свои функции получения погоды и генерации рекомендации
# Если они лежат в recommendations.views, импорт будет таким:
from recommendations.views import get_weather_data, get_geomagnetic_data, get_pollen_data, generate_smart_recommendation

def global_smart_recommendation(request):
    """Глобально добавляет smart_recommendation на все страницы для авторизованных пользователей"""
    if not request.user.is_authenticated:
        return {}

    today_date = date.today()
    
    # 1. Получаем задачи текущего юзера на сегодня
    tasks_list = Tasks.objects.filter(
        user=request.user,
        start_time__date=today_date
    ).order_by('start_time')
    
    # 2. Получаем данные из API
    real_weather = get_weather_data()
    geo_storm = get_geomagnetic_data()
    pollen = get_pollen_data(real_weather)
    
    # 3. Генерируем рекомендацию
    smart_rec = generate_smart_recommendation(request.user, tasks_list, real_weather, geo_storm, pollen)
    
    # Этот словарь станет доступен во ВСЕХ шаблонах (.html) сайта автоматически
    return {
        'smart_recommendation': smart_rec
    }