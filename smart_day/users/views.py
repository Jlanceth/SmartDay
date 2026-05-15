from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm, UserUpdateForm, UserProfile


def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST) # Используем новую форму
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('users:profile')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):

    if request.method == 'POST':

        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():

            user = form.get_user()

            login(request, user)

            return redirect('/')

    else:
        form = AuthenticationForm()

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


@login_required
def settings_view(request):
    # Получаем профиль пользователя (создаем, если его еще нет)
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=profile)
        
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