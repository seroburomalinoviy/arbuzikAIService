from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator


class User(models.Model):
    telegram_id = models.CharField('telegram id', max_length=250, unique=True, editable=False, blank=False)
    user_name = models.CharField('user name', max_length=250, blank=True, editable=False, unique=False)
    subscription_status = models.CharField('Sub status', max_length=200, blank=False, unique=False, editable=True)
    subscription_final_date = models.DateTimeField('subscription final date', default=timezone.now)
    subscription_usage_limit = models.IntegerField('days limit', default=1, validators=[MinValueValidator(0)])
    tune = models.CharField('tune', max_length=300, blank=True, editable=True, unique=False, null=True)
    subscription = models.ForeignKey('Subscription', on_delete=models.CASCADE)

    def __str__(self):
        return self.user_name

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'


class Subscription(models.Model):
    name = models.CharField('sub name', max_length=250, blank=False, editable=True, unique=False)
    time_voice_limit = models.IntegerField('limit of voice\'s time', default=30, blank=False, editable=True, validators=[MinValueValidator(0)])
    price = models.FloatField('price of sub', default=1.0, blank=False, editable=True, validators=[MinValueValidator(0.0)])
    days_limit = models.IntegerField('limit of days', default=1, blank=False, null=True, editable=True)
    voices = models.ForeignKey('Voice', on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'subscription'
        verbose_name_plural = 'subscriptions'


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
        blank=True
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE
    )
    subcategory = models.ForeignKey(
        'Subcategory',
        on_delete=models.CASCADE
    )
    image = models.ImageField(
        'Image',
        upload_to='images/',  # need set
        editable=True,
        null=True,
        blank=True
    )
    file_path = models.FilePathField(
        'voice file',
        path='voices/',  # need set
        allow_folders=True
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

    class Meta:
        verbose_name = 'Subcategory'
        verbose_name_plural = 'Subcategories'

    def __str__(self):
        return self.title

