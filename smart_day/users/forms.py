from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile
from django.contrib.auth.forms import AuthenticationForm

# 1. Форма регистрации
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(label="Адрес электронной почты")

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)

# 2. Форма для основных данных (Модель User)
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(label="Адрес электронной почты")
    first_name = forms.CharField(label="Имя", required=False)
    last_name = forms.CharField(label="Фамилия", required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

# 3. Форма для параметров планирования (Модель UserProfile)
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'avatar',
            'has_pollen_allergy', 
            'has_dust_allergy', 
            'has_sun_allergy', 
            'magnetic_sensitivity', 
            'preferred_notification_time'
        ]
        widgets = {
            'preferred_notification_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'magnetic_sensitivity': forms.Select(attrs={'class': 'form-select'}),
        }


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Email или имя пользователя",
        widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'})
    )