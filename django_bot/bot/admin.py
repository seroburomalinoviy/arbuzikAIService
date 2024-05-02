from django.contrib import admin
from .models import Category, Voice, Subcategory, Subscription, MediaData


class SubcategoryInline(admin.TabularInline):
    model = Subcategory


@admin.register(MediaData)
class MediaDataAdmin(admin.ModelAdmin):
    empty_value_display = "<пусто>"
    list_display = ['slug']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    empty_value_display = "<пусто>"
    list_display = ['title', 'subscription']
    search_fields = ['title']
    inlines = [SubcategoryInline]


@admin.register(Voice)
class VoiceAdmin(admin.ModelAdmin):
    empty_value_display = "<пусто>"
    list_display = ['title', 'subcategory', 'category_display', 'subscription_display']
    search_fields = ['title', 'description']

    @admin.display(description='Category', ordering='subcategory__category__title')
    def category_display(self, obj):
        return str(obj.subcategory.category.title)

    @admin.display(description='Subscription', ordering='subcategory__category__subscription__title')
    def subscription_display(self, obj):
        return str(obj.subcategory.category.subscription.title)


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    empty_value_display = "<пусто>"
    list_display = ['title', 'category', 'subscription_display']
    search_fields = ['title', 'slug']

    @admin.display(description='Subscription', ordering='category__subscription__title')
    def subscription_display(self, obj):
        return str(obj.category.subscription.title)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    empty_value_display = "<пусто>"
    list_display = ['title', 'time_voice_limit', 'days_limit', 'price']

