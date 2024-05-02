from django.contrib import admin
from django.db import models
from django.contrib import messages

from config.settings import MEDIA_ROOT
from .models import VoiceParser, SubscriptionParser
from .utils import subscription_parser, voice_parser


@admin.register(VoiceParser)
class VoiceParserAdmin(admin.ModelAdmin):
    empty_value_display = "<пусто>"
    list_display = ['date']

    def save_model(self, request, obj: VoiceParser, form, change):
        super().save_model(request, obj, form, change)

        csv_file_rel_path: models.FileField = obj.csv_file
        csv_file_path = str(MEDIA_ROOT) + '/' + str(csv_file_rel_path)
        try:
            message = voice_parser(csv_file_path)
            messages.add_message(request, messages.INFO, message)
        except Exception as e:
            messages.add_message(request, messages.WARNING, e)


@admin.register(SubscriptionParser)
class SubscriptionParserAdmin(admin.ModelAdmin):
    empty_value_display = "<пусто>"
    list_display = ['date']

    def save_model(self, request, obj: SubscriptionParser, form, change):
        super().save_model(request, obj, form, change)
        csv_file_rel_path: models.FileField = obj.csv_file
        csv_file_path = str(MEDIA_ROOT) + '/' + str(csv_file_rel_path)
        try:
            message = subscription_parser(csv_file_path)
            messages.add_message(request, messages.INFO, message)
        except Exception as e:
            messages.add_message(request, messages.WARNING, e)

