from django.shortcuts import render
from django.http import HttpResponse


def current_weather_view(request):
    return HttpResponse("Current weather page")


def weather_forecast_view(request):
    return HttpResponse("Weather forecast page")