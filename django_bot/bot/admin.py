from django.contrib import admin
from .models import Category, Voice, Subcategory, Subscription


class SubcategoryInline(admin.TabularInline):
    model = Subcategory


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    empty_value_display = "<пусто>"
    list_display = ['title']
    search_fields = ['title']
    inlines = [SubcategoryInline]


@admin.register(Voice)
class VoiceAdmin(admin.ModelAdmin):
    empty_value_display = "<пусто>"
    search_fields = ['title', 'description']
    list_filter = ['subcategory', 'subcategory__category__title']


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    empty_value_display = "<пусто>"
    list_display = ['title', 'category']
    search_fields = ['title', 'slug']
    list_filter = ['category']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    empty_value_display = "<пусто>"
    list_display = ['title', 'time_voice_limit', 'days_limit', 'price']

