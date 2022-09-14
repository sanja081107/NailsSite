from celery import shared_task
from django.core.mail import send_mail
from celery.schedules import crontab
from .models import *


@shared_task(name="order_created")
def order_created(arg):
    """
    Задача для отправки уведомления по электронной почте при успешном создании заказа.
    """
    post_id = arg
    post = Post.objects.get(id=post_id)
    subject = 'Your order {}'.format(post.title)
    message = 'Dear {},\nYou have successfully placed an order.\nYour time is {}.'.format(post.client.first_name, post.title)

    email = send_mail(subject, message, 'sanja081107@gmail.com', [post.client.email])

    return email

@shared_task
def order_canceled(arg):
    """
    Задача для отправки уведомления по электронной почте при отмене заказа.
    """
    post = Post.objects.get(id=arg)
    subject = 'Canceled order'
    message = 'Dear {},\nYou have successfully canceled.'.format(post.client.first_name,)

    email = send_mail(subject, message, 'sanja081107@gmail.com', [post.client.email])

    return email


