from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm


def register_view(request):

    if request.method == 'POST':

        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(request, user)

            return redirect('/')

    else:
        form = UserCreationForm()

    return render(
        request,
        'users/register.html',
        {'form': form}
    )


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

    return render(
        request,
        'users/settings.html'
    )