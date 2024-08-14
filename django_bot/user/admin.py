from django.contrib import admin

from .models import User, Order


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


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    empty_value_display = "<пусто>"
    list_display = [
        "telegram_username",
        "status",
        "amount",
        "currency"
        "subscription_title"
    ]

    @admin.display(description='Пользователь')
    def telegram_username(self, obj):
        return str(obj.user.telegram_username)

    @admin.display(description='Подписка')
    def subscription_title(self, obj):
        return str(obj.subscription.title)



