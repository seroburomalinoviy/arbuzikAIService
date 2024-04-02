import os
from dotenv import load_dotenv

from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.files.storage import FileSystemStorage
from django.conf import settings

load_dotenv()


class OverwriteStorage(FileSystemStorage):
    """
    Custom file system storage: Overwrite get_available_name to make Django replace files instead of
    creating new ones over and over again.
    """
    def get_available_name(self, name, max_length=None):
        self.delete(name)
        return super().get_available_name(name, max_length)


class User(models.Model):
    telegram_id = models.CharField(
        'telegram id',
        max_length=250,
        primary_key=True
    )
    nick_name = models.CharField(
        'telegram nick name',
        max_length=100
    )
    user_name = models.CharField(
        'telegram username',
        max_length=100
    )
    subscription_status = models.CharField(
        'Статус подписки',
        max_length=200,
        editable=True
    )
    subscription_final_date = models.DateTimeField(
        'Дата окончания подписки',
        # default=timezone.now
    )
    subscription_usage_limit = models.IntegerField(
        'Осталось до конце подписки',
        default=1,
        validators=[MinValueValidator(0)]
    )
    pitch = models.IntegerField(
        'Pitch',
        default=0,
        validators=[MinValueValidator(-150), MaxValueValidator(150)],
        blank=True,
        editable=True,
        null=True
    )
    subscription = models.ForeignKey(
        'Subscription',
        null=True,
        on_delete=models.SET_NULL
    )
    voices = models.ManyToManyField('Voice')

    def __str__(self):
        return self.nick_name

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Subscription(models.Model):
    title = models.CharField(
        'Название подписки',
        max_length=250,
        editable=True,
        unique=True
        )
    time_voice_limit = models.IntegerField(
        'Ограничение аудиофайла, сек',
        default=30,
        editable=True,
        validators=[MinValueValidator(0)]
    )
    price = models.FloatField(
        'Цена',
        default=1.0,
        editable=True,
        validators=[MinValueValidator(-1.0)]
    )
    days_limit = models.IntegerField(
        'Дней в подписке',
        default=1, # поставил бы 0
        editable=True
    )
    image_cover = models.ImageField('Обложка подписки')
    available_voices = models.ManyToManyField('Voice')
    available_categories = models.ManyToManyField('Category')
    available_subcategories = models.ManyToManyField('Subcategory')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'


class Voice(models.Model):
    gender_choice = [
        ('male', 'Male'),
        ('female', 'Female')
    ]

    title = models.CharField(
        'Название голоса',
        max_length=200,
        editable=True
    )
    description = models.TextField(
        'Описание голоса',
        max_length=400,
        editable=True,
        blank=True,
        default='Описание'
    )
    subcategory = models.ForeignKey(
        'Subcategory',
        on_delete=models.SET_NULL,
        null=True
    )
    image = models.ImageField(
        'Картинка',
        upload_to='covers/',
        editable=True,
        null=True,
        blank=True
    )
    model_pth = models.FileField(
        'Файл pth',
        upload_to='voices/',
        editable=True,
        null=True,
        blank=True,  # todo: change on Prod
        storage=OverwriteStorage()
    )
    model_index = models.FileField(
        'Файл index',
        upload_to='voices/',
        editable=True,
        null=True,
        blank=True,  # todo: change on Prod
        storage=OverwriteStorage()
    )
    gender = models.CharField(
        'Пол',
        choices=gender_choice,
        max_length=10,
        default='Male'
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Голос'
        verbose_name_plural = 'Голоса'


class Category(models.Model):
    title = models.CharField(
        'Название категории',
        max_length=200,
        editable=True,
        unique=True
    )
    description = models.TextField(
        'Description',
        max_length=500,
        editable=True,
        default='Описание'
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Subcategory(models.Model):
    title = models.CharField(
        'Название подкатегории',
        max_length=200,
        editable=True,
        unique=True
    )
    slug = models.SlugField(
        'slug',
        unique=True
    )
    category = models.ForeignKey(
        'Category',
        blank=True,
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'

    def __str__(self):
        return self.title

