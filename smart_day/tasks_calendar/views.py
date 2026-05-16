from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import TaskForm
from .models import Tasks


@login_required
def task_list_view(request):
    tasks = Tasks.objects.filter(user=request.user).order_by('start_time')
    
    return render(request, 'tasks_calendar/list.html', {'tasks': tasks})


@login_required
def task_create_view(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user  # Привязываем к юзеру
            task.save()
            return redirect('tasks_calendar:list')
    else:
        form = TaskForm()
    
    return render(request, 'tasks_calendar/task_form.html', {'form': form})

# Просмотр одной задачи
def task_detail_view(request, task_id):
    task = get_object_or_404(Tasks, id=task_id, user=request.user)
    return render(request, 'tasks_calendar/detail.html', {'task': task})

# Обновление
def task_update_view(request, task_id):
    task = get_object_or_404(Tasks, id=task_id, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('tasks_calendar:list')
    else:
        form = TaskForm(instance=task)
    
    # Передаем edit_mode здесь:
    return render(request, 'tasks_calendar/task_form.html', {
        'form': form, 
        'edit_mode': True
    })

# Удаление
def task_delete_view(request, task_id):
    task = get_object_or_404(Tasks, id=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks_calendar:list')
    return render(request, 'tasks_calendar/confirm_delete.html', {'task': task})