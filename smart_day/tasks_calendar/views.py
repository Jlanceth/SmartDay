import requests
import os
import json
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import TaskForm
from .models import Tasks
from django.views.decorators.http import require_POST
from dateutil.parser import parse
from django.utils import timezone

# Реальный тестовый эндпоинт, который возвращает массив JSON-задач
EXTERNAL_CALENDAR_API_URL = os.path.join(settings.BASE_DIR, 'calendar_plans.json')

def fetch_external_tasks():
    """Читает планы из локального JSON-файла, имитируя внешнее API, с поддержкой таймзон"""
    try:
        with open(EXTERNAL_CALENDAR_API_URL, 'r', encoding='utf-8') as f:
            external_data = json.load(f)
            
            normalized_tasks = []
            for item in external_data:
                # 1. Парсим строку в объект datetime
                start_time = parse(item.get('start_time'))
                
                # 2. Если у даты нет часового пояса, делаем её aware (привязываем к текущей таймзоне проекта)
                if timezone.is_naive(start_time):
                    start_time = timezone.make_aware(start_time, timezone.get_current_timezone())
                
                normalized_tasks.append({
                    'id': item.get('id'),
                    'title': item.get('title'),
                    'description': item.get('description', ''),
                    'start_time': start_time,
                    'location': item.get('location', ''),
                    'task_type': item.get('task_type', 'other'),
                    'is_external': True,
                })
            return normalized_tasks
    except Exception as e:
        print(f"[EXTERNAL API ERROR] Не удалось прочитать файл планов: {e}")
    return []


@login_required
def task_list_view(request):
    # 1. Получаем твои локальные задачи из базы данных (упорядоченные по времени)
    local_tasks = Tasks.objects.filter(user=request.user).order_by('start_time')
    
    # 2. Получаем внешние задачи через реальный HTTP-запрос
    external_tasks = fetch_external_tasks()
    
    # 3. Объединяем QuerySet локальных задач и список внешних словарей в один общий список
    combined_tasks = list(local_tasks) + external_tasks
    
    # 4. Сортируем абсолютно все задачи по времени начала (чтобы внешние планы встали строго на свои места между локальными)
    combined_tasks.sort(key=lambda x: x.start_time if hasattr(x, 'start_time') else x['start_time'])
    
    return render(request, 'tasks_calendar/list.html', {'tasks': combined_tasks})


@login_required
def task_create_view(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('tasks_calendar:list')
    else:
        form = Form = TaskForm()
    return render(request, 'tasks_calendar/task_form.html', {'form': form})


@login_required
def task_detail_view(request, task_id):
    # Просмотр деталей оставляем только для локальных задач из БД
    task = get_object_or_404(Tasks, id=task_id, user=request.user)
    return render(request, 'tasks_calendar/detail.html', {'task': task})


@login_required
def task_update_view(request, task_id):
    task = get_object_or_404(Tasks, id=task_id, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('tasks_calendar:list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks_calendar/task_form.html', {'form': form, 'edit_mode': True})


@login_required
def task_delete_view(request, task_id):
    task = get_object_or_404(Tasks, id=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks_calendar:list')
    return render(request, 'tasks_calendar/confirm_delete.html', {'task': task})


@login_required
@require_POST
def bulk_delete_view(request):
    task_ids = request.POST.getlist('task_ids')
    if task_ids:
        # Удаляем только локальные задачи. Внешние не имеют чекбоксов, поэтому их ID сюда не придут
        Tasks.objects.filter(id__in=task_ids, user=request.user).delete()
    return redirect('tasks_calendar:list')