from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    empty_value_display = "<пусто>"
    list_display = [
        "telegram_username",
        "subscription",
        "subscription_status",
        "subscription_attempts",
        "subscription_final_date",
    ]
