# Generated by Django 4.2.8 on 2024-08-08 17:06

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("bot", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "telegram_id",
                    models.CharField(
                        max_length=250,
                        primary_key=True,
                        serialize=False,
                        verbose_name="telegram id",
                    ),
                ),
                (
                    "telegram_nickname",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        null=True,
                        verbose_name="telegram nick name",
                    ),
                ),
                (
                    "telegram_username",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        null=True,
                        verbose_name="telegram username",
                    ),
                ),
                (
                    "subscription_status",
                    models.BooleanField(default=False, verbose_name="Статус подписки"),
                ),
                (
                    "subscription_final_date",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        null=True,
                        verbose_name="Дата окончания подписки",
                    ),
                ),
                (
                    "subscription_attempts",
                    models.PositiveIntegerField(
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Количество попыток",
                    ),
                ),
                (
                    "pitch",
                    models.IntegerField(
                        blank=True,
                        default=0,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(-150),
                            django.core.validators.MaxValueValidator(150),
                        ],
                        verbose_name="Pitch",
                    ),
                ),
                (
                    "favorites",
                    models.ManyToManyField(
                        blank=True, to="bot.voice", verbose_name="Избранные голоса"
                    ),
                ),
                (
                    "subscription",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="users",
                        to="bot.subscription",
                    ),
                ),
            ],
            options={
                "verbose_name": "Пользователь",
                "verbose_name_plural": "Пользователи",
            },
        ),
    ]
