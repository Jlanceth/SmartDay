from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import date
from tasks_calendar.models import Tasks


@login_required
def index_view(request):
    today_date = date.today()
    
    tasks_list = Tasks.objects.filter(
        user=request.user,
        start_time__date=today_date
    ).order_by('start_time')
    
    context = {
        'today': today_date,
        'tasks': tasks_list,
        'weather': {'temp': 22, 'condition': 'Солнечно', 'city': 'Пермь'},
    }
    return render(request, 'main/index.html', context)