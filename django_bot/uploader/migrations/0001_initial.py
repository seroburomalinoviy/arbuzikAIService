# Generated by Django 4.2.8 on 2024-08-07 07:56

import bot.models
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SubscriptionParser",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "csv_file",
                    models.FileField(
                        storage=bot.models.OverwriteStorage(),
                        upload_to="csv/",
                        verbose_name="CSV file",
                    ),
                ),
                (
                    "date",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created"),
                ),
            ],
            options={
                "verbose_name": "Загрузить подписки",
                "verbose_name_plural": "Загрузить подписки",
            },
        ),
        migrations.CreateModel(
            name="VoiceParser",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "csv_file",
                    models.FileField(
                        storage=bot.models.OverwriteStorage(),
                        upload_to="csv/",
                        verbose_name="CSV file",
                    ),
                ),
                (
                    "date",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created"),
                ),
            ],
            options={
                "verbose_name": "Загрузить голооса",
                "verbose_name_plural": "Загрузить голоса",
            },
        ),
    ]
