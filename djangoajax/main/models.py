from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import *
from django.urls import reverse


class Post(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название', unique=True, validators=[RegexValidator(regex=r'\.$', message='Model error')])
    client = models.ForeignKey('CustomUser', on_delete=models.PROTECT, verbose_name='Клиент', default=None, blank=True, null=True)
    service = models.ForeignKey('Service', on_delete=models.PROTECT, verbose_name='Доступные услуги', default=None, blank=True, null=True)
    date = models.DateField(verbose_name='Дата', default=None)
    is_active = models.BooleanField(verbose_name='Опубликовать', default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Time'
        verbose_name_plural = 'Times'
        ordering = ['date']


class Service(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название', validators=[RegexValidator(regex=r'$', message='Model error')])

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        ordering = ['id']


class CustomUser(AbstractUser):
    photo = models.ImageField(upload_to='photos/%Y/%m/%d/', verbose_name='Фото', null=True, blank=True)
    birthday = models.DateField(verbose_name='День рождения', null=True, blank=True)
    instagram = models.CharField(max_length=50, verbose_name='Инстаграм', null=True, blank=True)
    mobile = models.CharField(max_length=13, verbose_name='Телефон', null=True, blank=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def get_absolute_url(self):
        return reverse('user_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.username
