# Generated by Django 4.0.7 on 2022-09-21 12:07

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_myworks_alter_profitformonth_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customuser',
            options={'verbose_name': 'Пользователь', 'verbose_name_plural': 'Мои пользователи'},
        ),
        migrations.AlterModelOptions(
            name='myworks',
            options={'ordering': ['-date', 'title'], 'verbose_name': 'Работа', 'verbose_name_plural': 'Мои работы'},
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-date', 'title'], 'verbose_name': 'Запись', 'verbose_name_plural': 'Записи на ногти'},
        ),
        migrations.AlterModelOptions(
            name='profitformonth',
            options={'ordering': ['-date', 'title'], 'verbose_name': 'Доход за месяц', 'verbose_name_plural': 'Доход за месяц'},
        ),
        migrations.AlterModelOptions(
            name='service',
            options={'ordering': ['id'], 'verbose_name': 'Услуга', 'verbose_name_plural': 'Мои услуги'},
        ),
        migrations.AlterField(
            model_name='myworks',
            name='date',
            field=models.DateField(blank=True, default=datetime.datetime(2022, 9, 21, 12, 7, 27, 276318, tzinfo=utc), null=True, verbose_name='Дата'),
        ),
        migrations.AlterField(
            model_name='myworks',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='photos/%Y/%m/%d/', verbose_name='Фото работы'),
        ),
    ]
