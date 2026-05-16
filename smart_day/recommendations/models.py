from django.db import models
from django.contrib.auth.models import User
from tasks_calendar.models import Tasks


class Recommendation(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recommendations'
    )

    task = models.ForeignKey(
        Tasks,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    message = models.TextField()

    generated_at = models.DateTimeField(
        auto_now_add=True
    )

    weather_summary = models.CharField(
        max_length=255
    )

    recommendation_type = models.CharField(
        max_length=100,
        blank=True
    )

    def __str__(self):
        return f"Recommendation for {self.user.username}"