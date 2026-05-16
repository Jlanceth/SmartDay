from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def notification_list_view(request):
    # Страница со списком всех уведомлений (если планируется хранить их в БД)
    return render(request, 'notifications/list.html')

@login_required
def send_test_notification_view(request):
    """Генерирует быстрое тестовое всплывающее окно для проверки связи"""
    messages.info(request, "Тестовое уведомление: Адаптивная система SmartDay работает в штатном режиме!")
    # Перенаправляем обратно на ту страницу, с которой пользователь нажал кнопку
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def notification_settings_view(request):
    # Страница настроек (время пушей, типы уведомлений)
    return render(request, 'notifications/settings.html')