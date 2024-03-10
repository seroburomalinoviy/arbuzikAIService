from django.contrib import admin
from .models import Category, Voice, Subcategory, User


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
    list_display = ['nick_name', 'subscription_status', 'subscription_final_date']


