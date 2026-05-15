from django.db import models


class WeatherData(models.Model):

    city = models.CharField(
        max_length=100
    )

    temperature = models.FloatField()

    humidity = models.IntegerField()

    weather_condition = models.CharField(
        max_length=100
    )

    wind_speed = models.FloatField()

    k_index = models.FloatField(
        null=True,
        blank=True
    )

    pollen_level = models.CharField(
        max_length=50,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.city} - {self.temperature}°C"