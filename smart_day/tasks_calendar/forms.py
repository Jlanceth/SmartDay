from django import forms
from .models import Tasks

class TaskForm(forms.ModelForm):
    class Meta:
        model = Tasks
        fields = [
            'title', 'description', 'location', 
            'task_type', 'is_outdoor', 'start_time', 'end_time'
        ]
        labels = {
            'title': 'Название задачи',
            'description': 'Описание',
            'location': 'Местоположение',
            'task_type': 'Тип активности',
            'is_outdoor': 'На свежем воздухе',
            'start_time': 'Время начала',
            'end_time': 'Время завершения',
        }
        widgets = {
            'start_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M'
            ),
            'end_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M'
            ),
            'description': forms.Textarea(attrs={'rows': 3}),
            'task_type': forms.Select(attrs={'class': 'form-select'}),
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['start_time'].input_formats = ['%Y-%m-%dT%H:%M']
            self.fields['end_time'].input_formats = ['%Y-%m-%dT%H:%M']