from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),

    # Смена пароля (когда пользователь вошел)
    path('password-change/', 
        auth_views.PasswordChangeView.as_view(
            template_name='users/password_change.html',
            success_url=reverse_lazy('users:password_change_done') # Добавили успех
        ), 
        name='password_change'),

    path('password-change/done/', 
        auth_views.PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'), 
        name='password_change_done'),

    # Сброс пароля (когда пароль забыт)
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='users/password_reset.html',
             email_template_name='registration/password_reset_email.html', # можно оставить стандартным
             success_url=reverse_lazy('users:password_reset_done') # Указываем на users:
         ), 
         name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), 
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html',
             success_url=reverse_lazy('users:password_reset_complete') # Указываем на users:
         ), 
         name='password_reset_confirm'),
    
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), 
         name='password_reset_complete'),
]