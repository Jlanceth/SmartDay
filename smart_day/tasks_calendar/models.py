from django.db import models
from django.contrib.auth.models import User


class Tasks(models.Model):

    TASK_TYPES = [
        ('meeting', 'Встреча'),
        ('walk', 'Прогулка'),
        ('sport', 'Спорт'),
        ('study', 'Учеба'),
        ('other', 'Другое'),
    ]

    SOURCE_TYPES = [
        ('manual', 'Manual'),
        ('google', 'Google Calendar'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tasks'
    )

    title = models.CharField(
        max_length=255
    )

    description = models.TextField(
        blank=True
    )

    location = models.CharField(
        max_length=255,
        blank=True
    )

    is_outdoor = models.BooleanField(
        default=False
    )

    task_type = models.CharField(
        max_length=50,
        choices=TASK_TYPES,
        default='other'
    )

    source = models.CharField(
        max_length=20,
        choices=SOURCE_TYPES,
        default='manual'
    )

    start_time = models.DateTimeField()

    end_time = models.DateTimeField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.title