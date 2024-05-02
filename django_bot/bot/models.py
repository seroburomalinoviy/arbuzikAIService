from dotenv import load_dotenv

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.files.storage import FileSystemStorage

load_dotenv()


class OverwriteStorage(FileSystemStorage):
    """
    Custom file system storage: Overwrite get_available_name to make Django replace files instead of
    creating new ones over and over again.
    """
    def get_available_name(self, name, max_length=None):
        self.delete(name)
        return super().get_available_name(name, max_length)


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
        default=0,
        editable=True
    )
    image_cover = models.ImageField(
        'Обложка подписки', 
        blank=True
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'


class MediaData(models.Model):
    slug = models.SlugField(
        'Voice slug',
        unique=True
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
    demka = models.FileField(
        'Демка',
        upload_to='voices/',
        editable=True,
        null=True,
        blank=True,  # todo: change on Prod
        storage=OverwriteStorage()
    )


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
    image = models.ImageField(
        'Картинка',
        upload_to='covers/',
        editable=True,
        null=True,
        blank=True
    )
    gender = models.CharField(
        'Пол',
        choices=gender_choice,
        max_length=10,
        default='Male'
    )
    media_data = models.ManyToManyField(
        'MediaData'
    )
    subcategory = models.ForeignKey(
        'Subcategory',
        on_delete=models.CASCADE,
        related_name='voices'
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
        editable=True
    )
    description = models.TextField(
        'Description',
        max_length=500,
        editable=True,
        default='Описание'
    )
    subscription = models.ForeignKey(
        'Subscription',
        on_delete=models.CASCADE,
        related_name='categories'
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
        editable=True
    )
    slug = models.SlugField(
        'slug',
        unique=True
    )
    category = models.ForeignKey(
        'category',
        on_delete=models.CASCADE,
        related_name='subcategories'
    )

    class Meta:
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'

    def __str__(self):
        return self.title

