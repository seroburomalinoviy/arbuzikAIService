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
    list_display = ['title', 'subcategory', 'category_display']
    search_fields = ['title', 'description']
    list_filter = ['subcategory__category__title', 'subcategory__title']

    @admin.display(description='Category', ordering='subcategory__category__title')
    def category_display(self, obj):
        return str(obj.subcategory.category.title)


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    empty_value_display = "<пусто>"
    list_display = ['title', 'category']
    search_fields = ['title', 'slug']
    list_filter = ['category__title']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    empty_value_display = "<пусто>"
    list_display = ['title', 'time_voice_limit', 'days_limit', 'price']

