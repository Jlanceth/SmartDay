from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list_view, name='list'),

    path('send-test/', views.send_test_notification_view, name='send_test'),

    path('settings/', views.notification_settings_view, name='settings'),
]