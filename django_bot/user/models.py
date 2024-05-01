from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from bot.models import Subscription
import os


class User(models.Model):
    telegram_id = models.CharField(
        'telegram id',
        max_length=250,
        primary_key=True,
    )
    telegram_nickname = models.CharField(
        'telegram nick name',
        max_length=100,
        blank=True,
        null=True,
    )
    telegram_username = models.CharField(
        'telegram username',
        max_length=100,
        blank=True,
        null=True,
    )
    subscription_status = models.BooleanField(
        'Статус подписки',
        editable=True,
        default=False
    )
    subscription_final_date = models.DateTimeField(
        'Дата окончания подписки',
        editable=True,
        null=True,
    )
    subscription_attempts = models.PositiveIntegerField(
        'Количество попыток',
        validators=[MinValueValidator(0)],
        editable=True,
        null=True
    )
    pitch = models.IntegerField(
        'Pitch',
        default=0,
        validators=[MinValueValidator(-150), MaxValueValidator(150)],  # todo check NN
        blank=True,
        editable=True,
        null=True
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        default=os.environ.get('DEFAULT_SUBSCRIPTION'),
        related_name='users',
        null=True
    )
    # favorites = models.ManyToManyField(
    #     'Voice',
    #     blank=True
    # )

    def __str__(self):
        return self.telegram_nickname

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

