from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from .forms import UserUpdateForm, UserProfileForm, UserRegisterForm, EmailAuthenticationForm
from .models import UserProfile

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('users:profile')
    else:
        form = UserRegisterForm()
    
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/')
    else:
        form = EmailAuthenticationForm()
    
    return render(
        request,
        'users/login.html',
        {'form': form}
    )


def logout_view(request):
    logout(request)
    return redirect('/')


@login_required
def profile_view(request):

    return render(
        request,
        'users/profile.html'
    )


class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'users/password_change.html'
    success_url = reverse_lazy('users:profile')


@login_required
def settings_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        # Обязательно добавляем request.FILES для обработки аватара
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('users:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)

    return render(request, 'users/settings.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

