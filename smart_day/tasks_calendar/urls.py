from django.urls import path
from . import views

app_name = 'tasks_calendar'

urlpatterns = [
    path('', views.task_list_view, name='list'),

    path('create/', views.task_create_view, name='create'),

    path('<int:task_id>/', views.task_detail_view, name='detail'),

    path('<int:task_id>/edit/', views.task_update_view, name='edit'),
    path('bulk-delete/', views.bulk_delete_view, name='bulk_delete'),
    path('<int:task_id>/delete/', views.task_delete_view, name='delete'),
]