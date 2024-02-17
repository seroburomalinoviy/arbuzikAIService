from django.contrib import admin
from .models import Category, Voice, Subcategory


@admin.register(Category)
class GenreAdmin(admin.ModelAdmin):
    empty_value_display = "-empty-"


@admin.register(Voice)
class GenreAdmin(admin.ModelAdmin):
    empty_value_display = "-empty-"
    list_display = ['title', 'subcategory']


@admin.register(Subcategory)
class GenreAdmin(admin.ModelAdmin):
    empty_value_display = "-empty-"
    list_display = ['title', 'categories']

