from django.db import models

from bot.models import (Subcategory, Category, Subscription, OverwriteStorage)


class VoiceParser(models.Model):
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE
    )
    subcategory = models.ForeignKey(
        Subcategory,
        on_delete=models.CASCADE
    )
    csv_file = models.FileField(
        'CSV',
        upload_to='csv/',
        editable=True,
        storage=OverwriteStorage()
    )



class SubscriptionParser(models.Model):
    csv_file = models.FileField(
        'CSV',
        upload_to='csv/',
        editable=True,
        storage=OverwriteStorage()
    )

    class Meta:
        verbose_name = 'Парсер подписок'
        verbose_name_plural = 'Парсер подписок'