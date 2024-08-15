# Generated by Django 4.2.8 on 2024-08-15 09:27

import bot.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Category",
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
                    "title",
                    models.CharField(max_length=200, verbose_name="Название категории"),
                ),
                (
                    "description",
                    models.TextField(
                        max_length=500, null=True, verbose_name="Description"
                    ),
                ),
            ],
            options={
                "verbose_name": "Категория",
                "verbose_name_plural": "Категории",
            },
        ),
        migrations.CreateModel(
            name="Subcategory",
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
                    "title",
                    models.CharField(
                        max_length=200, verbose_name="Название подкатегории"
                    ),
                ),
                ("slug", models.SlugField(verbose_name="Subcategory slug")),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="subcategories",
                        to="bot.category",
                    ),
                ),
            ],
            options={
                "verbose_name": "Подкатегория",
                "verbose_name_plural": "Подкатегории",
            },
        ),
        migrations.CreateModel(
            name="Subscription",
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
                    "title",
                    models.CharField(
                        max_length=250, unique=True, verbose_name="Название подписки"
                    ),
                ),
                (
                    "telegram_title",
                    models.CharField(
                        max_length=500,
                        null=True,
                        verbose_name="Название подписки в боте",
                    ),
                ),
                ("description", models.TextField(max_length=1000, null=True)),
                (
                    "time_voice_limit",
                    models.IntegerField(
                        default=30,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Ограничение аудиофайла, сек",
                    ),
                ),
                (
                    "price",
                    models.FloatField(
                        default=1.0,
                        validators=[django.core.validators.MinValueValidator(-1.0)],
                        verbose_name="Цена",
                    ),
                ),
                (
                    "days_limit",
                    models.IntegerField(default=0, verbose_name="Дней в подписке"),
                ),
                (
                    "image_cover",
                    models.ImageField(
                        blank=True,
                        null=True,
                        storage=bot.models.OverwriteStorage(),
                        upload_to="data/",
                        verbose_name="Обложка подписки",
                    ),
                ),
            ],
            options={
                "verbose_name": "Подписка",
                "verbose_name_plural": "Подписки",
            },
        ),
        migrations.CreateModel(
            name="Voice",
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
                ("slug", models.SlugField(verbose_name="Voice slug")),
                ("image", models.URLField(verbose_name="Адрес картинки")),
                (
                    "model_pth",
                    models.FileField(
                        blank=True,
                        null=True,
                        storage=bot.models.OverwriteStorage(),
                        upload_to="data/",
                        verbose_name="Файл pth",
                    ),
                ),
                (
                    "model_index",
                    models.FileField(
                        blank=True,
                        null=True,
                        storage=bot.models.OverwriteStorage(),
                        upload_to="data/",
                        verbose_name="Файл index",
                    ),
                ),
                (
                    "demka",
                    models.FileField(
                        blank=True,
                        null=True,
                        storage=bot.models.OverwriteStorage(),
                        upload_to="data/",
                        verbose_name="Демка",
                    ),
                ),
                (
                    "title",
                    models.CharField(max_length=200, verbose_name="Название голоса"),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        max_length=400,
                        null=True,
                        verbose_name="Описание голоса",
                    ),
                ),
                (
                    "gender",
                    models.CharField(
                        choices=[("male", "Male"), ("female", "Female")],
                        default="Male",
                        max_length=10,
                        verbose_name="Пол",
                    ),
                ),
                (
                    "search_words",
                    models.TextField(
                        blank=True, null=True, verbose_name="Поисковые слова"
                    ),
                ),
                (
                    "subcategory",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="voices",
                        to="bot.subcategory",
                    ),
                ),
                ("subscriptions", models.ManyToManyField(to="bot.subscription")),
            ],
            options={
                "verbose_name": "Голос",
                "verbose_name_plural": "Голоса",
            },
        ),
    ]
