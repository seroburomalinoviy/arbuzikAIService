from django.db import models

from bot.models import Subscription, OverwriteStorage


class VoiceParser(models.Model):
    csv_file = models.FileField(
        'CSV file',
        upload_to='csv/',
        editable=True,
        storage=OverwriteStorage()
    )

    class Meta:
        verbose_name = 'Загрузить голооса'
        verbose_name_plural = 'Загрузить голоса'

    def __str__(self):
        return 'VoiceParser'


class SubscriptionParser(models.Model):
    csv_file = models.FileField(
        'CSV file',
        upload_to='csv/',
        editable=True,
        storage=OverwriteStorage()
    )

    class Meta:
        verbose_name = 'Загрузить подписки'
        verbose_name_plural = 'Загрузить подписки'

    def __str__(self):
        return 'SubscriptionParser'