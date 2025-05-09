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
        "date_created",
    ]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    empty_value_display = "<пусто>"
    search_fields = ["id"]
    list_display = [
        "id",
        "telegram_username",
        "status",
        "amount",
        "currency",
        "subscription_title",
        "created",
        "comment"
    ]

    @admin.display(description='Пользователь')
    def telegram_username(self, obj):
        if obj.user:
            return str(obj.user.telegram_username)
        else:
            return "неизвестен"

    @admin.display(description='Подписка')
    def subscription_title(self, obj):
        return str(obj.subscription.title)



