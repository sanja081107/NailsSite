from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import *
from django.urls import reverse
from django.utils import timezone


class Post(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название', validators=[RegexValidator(regex=r'$', message='Model error')])
    client = models.ForeignKey('CustomUser', on_delete=models.PROTECT, verbose_name='Клиент', default=None, blank=True, null=True)
    service = models.ForeignKey('Service', on_delete=models.PROTECT, verbose_name='Доступные услуги', default=None, blank=True, null=True)
    date = models.DateField(verbose_name='Дата', default=None)
    is_active = models.BooleanField(verbose_name='Опубликовать', default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи на ногти'
        ordering = ['-date', 'title']


class ProfitForMonth(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название месяца')
    profit = models.IntegerField(default=0, verbose_name='Прибыль за месяц')
    date = models.DateField(verbose_name='Дата', default=None)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Доход за месяц'
        verbose_name_plural = 'Доход за месяц'
        ordering = ['-date', 'title']


class MyWorks(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название работы')
    photo = models.ImageField(upload_to='photos/%Y/%m/%d/', verbose_name='Фото работы', null=True, blank=True)
    date = models.DateField(verbose_name='Дата', null=True, blank=True)
    is_active = models.BooleanField(verbose_name='Опубликовать', default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Работа'
        verbose_name_plural = 'Мои работы'
        ordering = ['-date', 'title']


class Service(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название', validators=[RegexValidator(regex=r'$', message='Model error')])
    price = models.IntegerField(default=0, verbose_name='Цена в рублях')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Мои услуги'
        ordering = ['id']


class CustomUser(AbstractUser):
    photo = models.ImageField(upload_to='photos/%Y/%m/%d/', verbose_name='Фото', null=True, blank=True)
    birthday = models.DateField(verbose_name='День рождения', null=True, blank=True)
    instagram = models.CharField(max_length=50, verbose_name='Инстаграм', null=True, blank=True)
    mobile = models.CharField(max_length=13, verbose_name='Телефон', null=True, blank=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Мои пользователи'

    def get_absolute_url(self):
        return reverse('user_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.username
