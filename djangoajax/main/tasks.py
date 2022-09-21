import json
from datetime import timedelta

from celery import shared_task
from django.core.mail import send_mail
import calendar

from django.http import JsonResponse

from .models import *


@shared_task(name="order_created")
def order_created(arg):
    """
    Задача для отправки уведомления по электронной почте при успешном создании заказа.
    """
    post_id = arg
    post = Post.objects.get(id=post_id)
    subject = 'Регистрация записи'
    message = 'Уважаемая(-ый) {},\nВы успешно оформили запись на ногти.\nВаше время {}.'.format(post.client.first_name, post.title)

    send_mail(subject, message, 'sanja081107@gmail.com', [post.client.email])

    return json.dumps({'created book': f'{post.title} - {post.client.username}'})


@shared_task
def order_canceled(arg):
    """
    Задача для отправки уведомления по электронной почте при отмене заказа.
    """
    post = Post.objects.get(id=arg)
    subject = 'Отмена записи'
    message = 'Уважаемая(-ый) {} {},\nВаша запись на {} была успешно отменена.'.format(post.client.first_name, post.client.last_name, post.title)

    send_mail(subject, message, 'sanja081107@gmail.com', [post.client.email])

    return json.dumps({'canceled book': f'{post.title} - {post.client.username}'})


@shared_task(name="profit_for_month")
def profit_for_month():
    """
    Задача для расчета прибыли за прошедший месяц (выполняется 1го числа каждого месяца).
    """
    today = datetime.date(datetime.now()) - timedelta(days=1)
    year = today.year
    month = today.month
    days_in_month = calendar.monthrange(year, month)[1]

    first_day = today - timedelta(today.day - 1)            # Первый день месяца
    last_day = first_day + timedelta(days_in_month - 1)     # Последний день месяца

    posts_all = Post.objects.all().order_by('date')
    posts_clients = []
    for el in posts_all:
        if el.client:
            posts_clients.append(el)                        # Список записей где есть клиент

    current_profit_for_last_month = [0]

    if posts_clients:
        for el in posts_clients:
            if first_day <= el.date <= last_day:
                current_profit_for_last_month.append(el.service.price)

    current_profit_for_last_month = sum(current_profit_for_last_month)

    post = ProfitForMonth.objects.create(title=f'{month}.{year}',
                                         profit=current_profit_for_last_month,
                                         date=today)

    return json.dumps({'profit for month': f'{post.title} - {post.profit} p.'})
