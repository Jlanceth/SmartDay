import requests
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import date
from datetime import datetime
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

            clouds = data.get('clouds', {}).get('all', 0)
            dynamic_uv = 1 if clouds > 80 else (3 if clouds > 40 else 5)

            return {
                'temp': round(data['main']['temp']),
                'condition': data['weather'][0]['description'].capitalize(),
                'condition_id': data['weather'][0]['id'],
                'wind_speed': data['wind']['speed'],
                'city': 'Пермь',
                'uv_index': dynamic_uv,
                'rain': data.get('rain', {}).get('1h', 0)
            }

    except requests.RequestException as e:
        print(f"[WEATHER ERROR] {e}")

    # запасные данные
    return {
        'temp': 20,
        'condition': 'Ясно',
        'condition_id': 800,
        'wind_speed': 2.0,
        'city': 'Пермь',
        'uv_index': 3,
        'rain': 0
    }


def get_geomagnetic_data():
    """Получение реального индекса магнитных бурь (Kp-index) от NOAA API"""
    url = "https://services.swpc.noaa.gov/json/planetary-k-index-by-3-hour.json"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data:
                latest_measure = data[-1]
                kp_value = float(latest_measure.get('kp_index', 0))
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
    return {'kp_index': 2, 'description': 'Нет данных'}


def get_pollen_data(weather):
    """Расчет уровня аллергенной опасности"""
    temp = weather['temp']
    wind_speed = weather['wind_speed']
    rain = weather['rain']
    month = datetime.now().month
    risk = 0
    # Сезонность
    if month == 4:
        risk += 2
    elif month == 5:
        risk += 3
    elif month == 6:
        risk += 3
    elif month == 7:
        risk += 2
    elif month == 8:
        risk += 2
    elif month == 9:
        risk += 1
    # Температура
    if temp >= 15:
        risk += 1
    # Ветер
    if wind_speed >= 5:
        risk += 1
    # Дождь снижает количество пыльцы
    if rain >= 2:
        risk -= 1
    risk = max(risk, 0)
    if risk >= 4:
        return {
            "is_blooming": True,
            "allergen_level": "Высокий",
            "birch_value": risk
        }
    elif risk >= 2:
        return {
            "is_blooming": True,
            "allergen_level": "Умеренный",
            "birch_value": risk
        }
    return {
        "is_blooming": False,
        "allergen_level": "Низкий",
        "birch_value": risk
    }



def generate_smart_recommendation(user, tasks, weather, geo_storm, pollen):
    """Динамическая генерация рекомендаций с жесткой привязкой к профилю текущего юзера"""
    recommendations = []
    
    # 1. ОПРЕДЕЛЯЕМ ПАРАМЕТРЫ ЗДОРОВЬЯ ИЗ ПРОФИЛЯ ПОЛЬЗОВАТЕЛЯ
    has_pollen_allergy = False
    has_dust_allergy = False
    has_sun_allergy = False
    high_magnetic_sensitivity = False
    
    profile = getattr(user, 'profile', None)
    if profile:
        has_pollen_allergy = profile.has_pollen_allergy
        has_dust_allergy = profile.has_dust_allergy
        has_sun_allergy = profile.has_sun_allergy

        high_magnetic_sensitivity = (
            profile.magnetic_sensitivity in ["medium", "high"]
        )

    # 2. АНАЛИЗИРУЕМ ТИПЫ ДЕЛА НА СЕГОДНЯ
    has_outdoor_tasks = False
    for task in tasks:
        # ИСПРАВЛЕНИЕ: Добавляем поиск по всем возможным именам полей уличной активности
        if (getattr(task, 'outdoor_activity', False) or 
            getattr(task, 'is_outdoor', False) or 
            getattr(task, 'outdoor', False)):
            has_outdoor_tasks = True
            break
            
        task_title = task.title.lower()
        task_category = str(getattr(task, 'category', '')).lower()
        # ИСПРАВЛЕНИЕ: Расширяем ключевые слова для уличных задач на случай опечаток
        if any(word in task_title for word in ['прогулка', 'гулять', 'улица', 'спорт', 'бег', 'парк']):
            has_outdoor_tasks = True
            break

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
        recommendations.append(
            "Сегодня у вас преимущественно домашние дела или учеба в помещении. "
            "За окном тепло, поэтому постарайтесь выделить время на проветривание комнаты."
        )

    # Блок В: Аллергены (Цветение / Пыль)
    # ИСПРАВЛЕНИЕ: Добавляем подстраховку: если уровень "Высокий", то считаем что blooming=True
    
    allergen_level = pollen.get('allergen_level', 'Низкий')

    if has_pollen_allergy:
        if allergen_level == "Высокий":
            recommendations.append(
                "⚠️ Сегодня ожидается высокий риск аллергенной активности. Рекомендуется принять антигистаминное средство и по возможности ограничить длительное пребывание на улице."
            )
        elif allergen_level == "Умеренный":
            recommendations.append(
                "🌿 Сегодня наблюдается умеренный риск аллергенной активности. При наличии чувствительности рекомендуется иметь при себе необходимые лекарственные средства."
            )
    
    if has_dust_allergy and weather['wind_speed'] >= 5.0:
        recommendations.append("⚠️ В городе ветрено, возможна высокая концентрация пыли в воздухе. Защищайте глаза и используйте спрей для носа.")

    # Блок Г: Солнечная активность (UV)
    if weather['uv_index'] >= 4:
        if has_sun_allergy:
            recommendations.append(
                f"🚨 Критический уровень опасности! У вас allergic на солнце, а УФ-индекс сегодня повышенный. "
                f"Обязательно нанесите защитный крем SPF50, наденьте головной убор или используйте зонт с UV-защитой."
            )
        else:
            recommendations.append("Солнечная активность повышена, при долгом нахождении на улице пригодятся солнцезащитные очки.")

    # Блок Д: Магнитные бури
    if geo_storm['kp_index'] >= 5:
        if high_magnetic_sensitivity:
            recommendations.append(
                f"🚨 Внимание! Зафиксирована сильная магнитная буря. "
                f"Учитывая вашу высокую метеочувствительность, "
                f"минимизируйте физические нагрузки, контролируйте давление и избегайте стрессовых задач."
            )
        else:
            recommendations.append("Наблюдаются умеренные геомагнитные возмущения. Метеозависимым людям рекомендуется соблюдать режим сна.")

    return " ".join(recommendations)

@login_required
def index_view(request):
    today_date = date.today()
    
    # 1. Получаем задачи текущего пользователя на сегодня
    tasks_list = Tasks.objects.filter(user=request.user, start_time__date=today_date).order_by('start_time')
    
    # 2. Собираем данные со всех трех API (Погода, Магнитные бури, Пыльца)
    real_weather = get_weather_data()
    geo_data = get_geomagnetic_data()
    pollen_data = get_pollen_data(real_weather)
    
    # 3. ВЫЗЫВАЕМ функцию генерации умных рекомендаций!
    # Она обработает профиль, задачи, погоду и соберет финальную строку
    smart_text = generate_smart_recommendation(
        user=request.user, 
        tasks=tasks_list, 
        weather=real_weather, 
        geo_storm=geo_data, 
        pollen=pollen_data
    )
    
    # 4. Передаем всё собранное (включая рекомендацию) в контекст шаблона
    context = {
        'today': today_date,
        'tasks': tasks_list,
        'weather': real_weather,
        'geo': geo_data,         # если пригодятся на главной
        'pollen': pollen_data,   # если пригодятся на главной
        'recommendation': smart_text,  # СЮДА ЗАПИСАЛСЯ НАШ СГЕНЕРИРОВАННЫЙ ТЕКСТ С АЛЛЕРГИЕЙ!
    }
    return render(request, 'main/index.html', context)