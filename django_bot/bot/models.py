from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class User(models.Model):
    telegram_id = models.CharField(
        'telegram id',
        max_length=250,
        unique=True
    )
    nick_name = models.CharField(
        'telegram nick name',
        max_length=100
    )
    user_name = models.CharField(
        'telegram user name',
        max_length=100
    )
    subscription_status = models.CharField(
        'Sub status',
        max_length=200,
        editable=True
    )
    subscription_final_date = models.DateTimeField(
        'subscription final date',
        # default=timezone.now
    )
    subscription_usage_limit = models.IntegerField(
        'days limit',
        default=1,
        validators=[MinValueValidator(0)]
    )
    pitch = models.IntegerField(
        'pitch',
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
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Subscription(models.Model):
    title = models.CharField(
        'subscription name',
        max_length=250,
        editable=True,
        unique=True
        )
    time_voice_limit = models.IntegerField(
        'limit time of voice in sec',
        default=30,
        editable=True,
        validators=[MinValueValidator(0)]
    )
    price = models.FloatField(
        'price',
        default=1.0,
        editable=True,
        validators=[MinValueValidator(-1.0)]
    )
    days_limit = models.IntegerField(
        'limit of days',
        default=1,
        editable=True
    )
    available_voices = models.ManyToManyField('Voice')
    available_categories = models.ManyToManyField('Category')
    available_subcategories = models.ManyToManyField('Subcategory')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'title'
        verbose_name_plural = 'titles'


class Voice(models.Model):
    gender_choice = [
        ('male', 'Male'),
        ('female', 'Female')
    ]

    title = models.CharField(
        'Voice title',
        max_length=200,
        editable=True
    )
    description = models.TextField(
        'Voice description',
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
        'Image',
        upload_to='images/',  # todo: set volume
        editable=True,
        null=True,
        blank=True
    )
    file_path = models.FilePathField(
        'voice file',
        path='/app/django_bot',  # todo: set volume
        allow_folders=True,
        null=True,
        blank=True  # todo: change on Prod
    )
    gender = models.CharField(
        'Gender',
        choices=gender_choice,
        max_length=10,
        default='Male'
    )

    def __str__(self):
        return self.title


class Category(models.Model):
    title = models.CharField(
        'Name',
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
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class Subcategory(models.Model):
    title = models.CharField(
        'Name',
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
        verbose_name = 'Subcategory'
        verbose_name_plural = 'Subcategories'

    def __str__(self):
        return self.title

