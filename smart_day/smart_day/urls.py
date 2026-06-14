from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
     path('admin/', admin.site.urls),
     path('', include('recommendations.urls')),
     path('users/', include('users.urls')),
     path('tasks/', include('tasks_calendar.urls')),
     path('weather/', include('weather.urls')),
     path('notifications/', include('notifications.urls')),
     path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    
     path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), 
         name='password_reset_complete'),

     path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), 
         name='password_reset_done'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)