from django.contrib import admin
from django.db import models
from .models import VoiceParser, SubscriptionParser

from django_bot.config.settings import MEDIA_ROOT


@admin.register(VoiceParser)
class VoiceParserAdmin(admin.ModelAdmin):
    pass

    # def save_model(self, request, obj: VoiceParser, form, change):
    #     super().save_model(request, obj, form, change)
    #
    #     csv_file_rel_path: models.FileField = obj.csv_file
    #     csv_file_path = str(MEDIA_ROOT) + '/' + str(csv_file_rel_path)


@admin.register(SubscriptionParser)
class SubscriptionParserAdmin(admin.ModelAdmin):
    pass






