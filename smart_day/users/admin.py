from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'has_pollen_allergy',
        'has_dust_allergy',
        'magnetic_sensitivity',
        'preferred_notification_time',
        'created_at',
    )

    list_filter = (
        'has_pollen_allergy',
        'has_dust_allergy',
        'magnetic_sensitivity',
    )

    search_fields = (
        'user__username',
    )
