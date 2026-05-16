import requests
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import date
from django.contrib import messages
from tasks_calendar.models import Tasks

WEATHER_API_KEY = '9fe4e13a07ddd935d3aa98e8ee5a85b9'
CITY_NAME = 'Perm'

LAT = 58.0105
LON = 56.2502


def get_weather_data():
    """Получение реальной погоды через OpenWeatherMap API"""
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY_NAME}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Вычисляем реалистичный UV-индекс динамически на основе облачности (clouds)
            clouds = data.get('clouds', {}).get('all', 0)
            dynamic_uv = 1 if clouds > 80 else (3 if clouds > 40 else 5)
            
            return {
                'temp': round(data['main']['temp']),
                'condition': data['weather'][0]['description'].capitalize(),
                'condition_id': data['weather'][0]['id'],
                'wind_speed': data['wind']['speed'],
                'city': 'Пермь',
                'uv_index': dynamic_uv
            }
    except requests.RequestException as e:
        print(f"[WEATHER ERROR] {e}")
    
    return {'temp': 29, 'condition': 'Ясно', 'condition_id': 800, 'wind_speed': 2.0, 'city': 'Пермь', 'uv_index': 5}


def get_geomagnetic_data():
    """Получение реального индекса магнитных бурь (Kp-index) от NOAA API"""
    url = "https://services.swpc.noaa.gov/json/planetary-k-index-by-3-hour.json"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data:
                # Берем самый последний элемент из списка (актуальное измерение)
                latest_measure = data[-1]
                kp_value = float(latest_measure.get('kp_index', 0))
                
                # Округляем до целого для нашей логики
                kp_index = round(kp_value)
                
                description = 'Геомагнитное поле спокойное'
                if kp_index >= 5:
                    description = 'Сильная магнитная буря (Шторм)'
                elif kp_index >= 4:
                    description = 'Небольшие геомагнитные возмущения'
                    
                return {
                    'kp_index': kp_index,
                    'description': description
                }
    except requests.RequestException as e:
        print(f"[GEOMAGNETIC API ERROR] {e}")
    # Безопасный дефолт, если упал внешний сервер
    return {'kp_index': 2, 'description': 'Нет данных'}


def get_pollen_data():
    """Получение реальных данных по цветению (аллергенам) от Open-Meteo Air Quality API"""
    url = f"https://api.open-meteo.com/v1/air-quality?latitude={LAT}&longitude={LON}&current=birch_pollen,grass_pollen"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            current_data = data.get('current', {})
            
            # Добавляем "or 0", чтобы защитить код от NoneType значений
            birch = current_data.get('birch_pollen')
            birch = float(birch) if birch is not None else 0.0
            
            grass = current_data.get('grass_pollen')
            grass = float(grass) if grass is not None else 0.0
            
            # Теперь сравнение никогда не упадет
            is_blooming = birch > 15 or grass > 10
            level = "Низкий"
            if birch > 100 or grass > 50:
                level = "Высокий"
            elif birch > 20 or grass > 10:
                level = "Умеренный"
                
            return {
                'is_blooming': is_blooming,
                'allergen_level': level,
                'birch_value': birch
            }
    except requests.RequestException as e:
        print(f"[POLLEN API ERROR] {e}")
    return {'is_blooming': False, 'allergen_level': 'Нет данных', 'birch_value': 0}



def generate_smart_recommendation(user, tasks, weather, geo_storm, pollen):
    """Динамическая генерация рекомендаций с жесткой привязкой к профилю текущего юзера"""
    recommendations = []
    
    # 1. ОПРЕДЕЛЯЕМ ПАРАМЕТРЫ ЗДОРОВЬЯ ИЗ ПРОФИЛЯ ПОЛЬЗОВАТЕЛЯ
    has_pollen_allergy = False
    has_dust_allergy = False
    has_sun_allergy = False
    high_magnetic_sensitivity = False
    
    # Пытаемся вытащить профиль текущего юзера
    profile = getattr(user, 'profile', None)
    
    if profile:
        # Приводим все заполненные аллергии в одну строку для удобного поиска по ключевым словам
        # Работает как с ManyToMany полями, так и с обычным текстовым/JSON полем
        allergies_str = ""
        if hasattr(profile, 'active_allergies'):
            # Если это связь ManyToMany или список объектов
            if hasattr(profile.active_allergies, 'all'):
                allergies_str = " ".join([str(a.name).lower() for a in profile.active_allergies.all()])
            else:
                allergies_str = str(profile.active_allergies).lower()
        
        # Задаем флаги на основе подстрок
        has_pollen_allergy = 'пыльца' in allergies_str or 'цветение' in allergies_str
        has_dust_allergy = 'пыль' in allergies_str and 'пыльца' not in allergies_str
        has_sun_allergy = 'солнце' in allergies_str or 'солнечная' in allergies_str or 'уф' in allergies_str
        
        # Проверяем влияние магнитных бурь
        magnetic_influence = ""
        if hasattr(profile, 'magnetic_influence'):
            magnetic_influence = str(profile.magnetic_influence).lower()
        elif hasattr(profile, 'influence_level'):  # если поле называется по-другому
            magnetic_influence = str(profile.influence_level).lower()
            
        high_magnetic_sensitivity = 'высокое' in magnetic_influence or 'сильное' in magnetic_influence

    # 2. АНАЛИЗИРУЕМ ТИПЫ ДЕЛА НА СЕГОДНЯ
    # Ищем, есть ли среди названий или категорий задач уличные активности
    has_outdoor_tasks = False
    for task in tasks:
        # Проверяем булево поле, если оно есть в твоей модели Tasks
        if getattr(task, 'outdoor_activity', False) or getattr(task, 'is_outdoor', False):
            has_outdoor_tasks = True
            break
        # Проверяем по ключевым словам в названии или категории ("прогулка", "гулять", "спорт")
        task_title = task.title.lower()
        task_category = str(getattr(task, 'category', '')).lower()
        if 'прогулка' in task_title or 'гулять' in task_title or 'прогулка' in task_category:
            has_outdoor_tasks = True

    # 3. СТРОИМ СИТУАТИВНЫЕ БЛОКИ РЕКОМЕНДАЦИЙ

    # Блок А: Базовая одежда по погоде
    is_raining = weather['condition_id'] < 600
    if is_raining:
        recommendations.append("На улице ожидается дождь — не забудьте взять зонт и надеть ветровку.")
    else:
        if weather['temp'] >= 25:
            recommendations.append("На улице очень жарко. Выбирайте максимально легкую одежду из натуральных тканей.")
        elif 15 <= weather['temp'] < 25:
            recommendations.append("Погода комфортная, можно надеть легкую кофту или футболку.")
        else:
            recommendations.append("На улице прохладно, не забудьте надеть куртку.")

    # Блок Б: Пересечение планов (Дом vs Улица)
    if has_outdoor_tasks:
        recommendations.append("У вас запланирована активность на свежем воздухе.")
        if weather['temp'] >= 25:
            recommendations.append("Обязательно возьмите с собой бутылку воды, чтобы избежать перегрева.")
    else:
        recommendations.append("Сегодня у вас преимущественно домашние дела или учеба в помещении. За окном тепло, поэтому постарайтесь выделить время на проветривание комнаты.")

    # Блок В: Аллергены (Цветение / Пыль)
    if has_pollen_allergy and pollen['is_blooming']:
        recommendations.append("⚠️ Так как у вас аллергия на цветение, перед выходом на улицу рекомендуется принять антигистаминное средство.")
    
    if has_dust_allergy and weather['wind_speed'] >= 5.0:
        recommendations.append("⚠️ В городе ветрено, возможна высокая концентрация пыли в воздухе. Защищайте глаза и используйте спрей для носа.")

    # Блок Г: Солнечная активность (UV)
    if weather['uv_index'] >= 4:
        if has_sun_allergy:
            recommendations.append("🚨 Критический уровень опасности! У вас аллергия на солнце, а УФ-индекс сегодня повышенный. Обязательно нанесите защитный крем SPF50, наденьте головной убор или используйте зонт с UV-защитой.")
        else:
            recommendations.append("Солнечная активность повышена, при долгом нахождении на улице пригодятся солнцезащитные очки.")

    # Блок Д: Магнитные бури
    if geo_storm['kp_index'] >= 5:
        if high_magnetic_sensitivity:
            recommendations.append("🚨 Внимание! Зафиксирована сильная магнитная буря. Учитывая ваше высокое метеочувствительность, минимизируйте физические нагрузки, контролируйте давление и избегайте стрессовых задач.")
        else:
            recommendations.append("Наблюдаются умеренные геомагнитные возмущения. Метеозависимым людям рекомендуется соблюдать режим сна.")

    # Склеиваем результат
    return " ".join(recommendations)


@login_required
def index_view(request):
    today_date = date.today()
    tasks_list = Tasks.objects.filter(user=request.user, start_time__date=today_date).order_by('start_time')
    
    real_weather = get_weather_data()
    
    context = {
        'today': today_date,
        'tasks': tasks_list,
        'weather': real_weather,
    }
    return render(request, 'main/index.html', context)