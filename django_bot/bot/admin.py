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
    list_display = ['title', 'subscription']
    search_fields = ['title', 'subscription']
    inlines = [SubcategoryInline]


@admin.register(Voice)
class GenreAdmin(admin.ModelAdmin):
    empty_value_display = "<пусто>"
    list_display = ['title', 'subcategory', 'category_display', 'subscription_display']

    @admin.display(description='Category', ordering='subcategory__category__title')
    def category_display(self, obj):
        return str(obj.subcategory.category.title)

    @admin.display(description='Subscription', ordering='subcategory__category__subscription__title')
    def category_display(self, obj):
        return str(obj.subcategory.category.subscription.title)


@admin.register(Subcategory)
class GenreAdmin(admin.ModelAdmin):
    empty_value_display = "<пусто>"
    list_display = ['title', 'category', 'subscription']
    search_fields = ['title', 'category', 'subscription']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    empty_value_display = "<пусто>"
    list_display = ['title', 'time_voice_limit', 'days_limit', 'price']

