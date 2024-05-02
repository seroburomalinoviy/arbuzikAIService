from django.contrib import admin
from .models import Category, Voice, Subcategory, Subscription, MediaData


class SubcategoryInline(admin.TabularInline):
    model = Subcategory


@admin.register(MediaData)
class MediaDataAdmin(admin.ModelAdmin):
    empty_value_display = "<пусто>"
    list_display = ['slug']


@admin.register(Category)
class GenreAdmin(admin.ModelAdmin):
    empty_value_display = "<пусто>"
    inlines = [SubcategoryInline]


@admin.register(Voice)
class GenreAdmin(admin.ModelAdmin):
    empty_value_display = "<пусто>"
    list_display = ['title', 'subcategory']


@admin.register(Subcategory)
class GenreAdmin(admin.ModelAdmin):
    empty_value_display = "<пусто>"
    list_display = ['title', 'category', 'slug']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    empty_value_display = "<пусто>"
    list_display = ['title', 'time_voice_limit', 'days_limit', 'price']

