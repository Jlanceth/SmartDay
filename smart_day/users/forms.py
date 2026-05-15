from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

# Форма регистрации (кастомизируем стандартную, чтобы добавить Email)
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(label="Адрес электронной почты")

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)

# Форма редактирования профиля в настройках
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(label="Адрес электронной почты")
    first_name = forms.CharField(label="Имя", required=False)
    last_name = forms.CharField(label="Фамилия", required=False)

    class Meta:
            model = UserProfile
            fields = [
                'has_pollen_allergy', 
                'has_dust_allergy', 
                'has_sun_allergy', 
                'magnetic_sensitivity', 
                'preferred_notification_time'
            ]
            widgets = {
                'preferred_notification_time': forms.TimeInput(attrs={'type': 'time'}),
                'magnetic_sensitivity': forms.Select(attrs={'class': 'form-select'}),
            }