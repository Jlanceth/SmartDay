from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import date
# Импортируй свои модели задач

@login_required
def index_view(request):
    # Здесь будет логика получения задач из базы
    tasks = [
        {'time': '09:00', 'title': 'Утренняя зарядка', 'category': 'Здоровье', 'duration': '30 мин', 'done': True},
        {'time': '10:00', 'title': 'Учеба', 'category': 'Университет', 'duration': '2 ч', 'done': False},
        # В реальном проекте это будет Task.objects.filter(user=request.user)
    ]
    
    context = {
        'today': date.today(),
        'tasks': tasks,
        'weather': {'temp': 22, 'condition': 'Солнечно', 'city': 'Пермь'}, # Пример данных
    }
    return render(request, 'main/index.html', context)