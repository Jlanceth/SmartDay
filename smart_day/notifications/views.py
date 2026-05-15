from django.shortcuts import render
from django.http import HttpResponse


def notification_list_view(request):
    return HttpResponse("Notification list page")


def send_test_notification_view(request):
    return HttpResponse("Send test notification page")


def notification_settings_view(request):
    return HttpResponse("Notification settings page")