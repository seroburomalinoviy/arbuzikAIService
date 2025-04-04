from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import os
import uuid

from bot.models import Subscription, Voice


def get_default_sub():
    return os.environ.get("DEFAULT_SUBSCRIPTION")


class User(models.Model):
    telegram_id = models.CharField(
        "telegram id",
        max_length=250,
        primary_key=True,
    )
    telegram_nickname = models.CharField(
        "telegram nick name",
        max_length=100,
        blank=True,
        null=True,
        default="unknown"
    )
    telegram_username = models.CharField(
        "telegram username",
        max_length=100,
        blank=True,
        null=True,
        default="unknown"
    )
    subscription_status = models.BooleanField(
        "Статус подписки", editable=True, default=False
    )
    subscription_final_date = models.DateTimeField(
        "Дата окончания подписки", editable=True, default=timezone.now, null=True
    )
    subscription_attempts = models.PositiveIntegerField(
        "Количество попыток",
        validators=[MinValueValidator(0)],
        editable=True,
        null=True,
    )
    pitch = models.IntegerField(
        "Pitch",
        default=0,
        validators=[MinValueValidator(-150), MaxValueValidator(150)],  # todo check NN
        blank=True,
        editable=True,
        null=True,
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        related_name="users",
        null=True
    )
    favorites = models.ManyToManyField(
        verbose_name="Избранные голоса",
        to=Voice,
        blank=True
    )
    date_created = models.DateTimeField(
        'Зарегистрирован',
        auto_now_add=True
    )

    def __str__(self):
        return str(self.telegram_id)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Order(models.Model):

    id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True
    )

    comment = models.TextField(
        verbose_name='Комментарий системы',
        null=True,
        blank=True
    )

    created = models.DateTimeField(
        'Заказ создан',
        auto_now_add=True
    )

    status = models.BooleanField(
        'Статус оплаты',
        null=True,
        blank=True
    )

    amount = models.FloatField(
        'Сумма',
        blank=True,
        null=True
    )

    currency = models.CharField(
        'Валюта',
        max_length=20,
        null=True,
        blank=True
    )

    user = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders'
    )

    subscription = models.ForeignKey(
        to=Subscription,
        on_delete=models.SET_NULL,
        null=True,
        related_name="orders"
    )

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = "Оплата подписок"
        verbose_name_plural = "Оплата подписок"

