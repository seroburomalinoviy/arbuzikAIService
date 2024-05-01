from django.contrib import admin
from .models import Category, Voice, Subcategory, User, Subscription
from parser.models import VoiceParser, SubscriptionParser


class SubcategoryInline(admin.TabularInline):
    model = Subcategory


@admin.register(Category)
class GenreAdmin(admin.ModelAdmin):
    empty_value_display = "-empty-"
    inlines = [SubcategoryInline]


@admin.register(Voice)
class GenreAdmin(admin.ModelAdmin):
    empty_value_display = "-empty-"
    list_display = ['title', 'subcategory']


@admin.register(Subcategory)
class GenreAdmin(admin.ModelAdmin):
    empty_value_display = "<пусто>"
    list_display = ['title', 'category', 'slug']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    empty_value_display = "<пусто>"
    list_display = ['telegram_nickname', 'subscription', 'subscription_status', 'subscription_final_date']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    empty_value_display = "<пусто>"
    list_display = ['title', 'time_voice_limit', 'days_limit', 'price']


@admin.register(VoiceParser)
class VoiceParserAdmin(admin.ModelAdmin):
    list_display = ['subscription']

    # def save_model(self, request, obj: VoiceParser, form, change):
    #     super().save_model(request, obj, form, change)
    #
    #     csv_file_rel_path: models.FileField = obj.csv_file
    #     csv_file_path = str(MEDIA_ROOT) + '/' + str(csv_file_rel_path)


@admin.register(SubscriptionParser)
class SubscriptionParserAdmin(admin.ModelAdmin):
    list_display = ['csv_file']







