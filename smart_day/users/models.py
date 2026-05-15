from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):

    MAGNETIC_SENSITIVITY_CHOICES = [
        ('low', 'Слабое влияние'),
        ('medium', 'Среднее влияние'),
        ('high', 'Сильное влияние'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    avatar = models.ImageField(
        upload_to='avatars/', 
        null=True, 
        blank=True, 
        verbose_name='Аватар'
    )

    has_pollen_allergy = models.BooleanField(
        default=False,
        verbose_name='Аллергия на пыльцу'
    )

    has_dust_allergy = models.BooleanField(
        default=False,
        verbose_name='Аллергия на пыль'
    )

    has_sun_allergy = models.BooleanField(
        default=False,
        verbose_name='Чувствительность к солнцу / УФ'
    )

    magnetic_sensitivity = models.CharField(
        max_length=10,
        choices=MAGNETIC_SENSITIVITY_CHOICES,
        default='low',
        verbose_name='Влияние магнитных бурь'
    )

    preferred_notification_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Время уведомления'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.user.username