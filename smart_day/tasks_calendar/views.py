from django.shortcuts import render
from django.http import HttpResponse


def task_list_view(request):
    return HttpResponse("Task list")


def task_create_view(request):
    return HttpResponse("Task create")


def task_detail_view(request, task_id):
    return HttpResponse(f"Task {task_id}")


def task_update_view(request, task_id):
    return HttpResponse(f"Update {task_id}")


def task_delete_view(request, task_id):
    return HttpResponse(f"Delete {task_id}")