from celery import shared_task
from django.core.mail import send_mail
from celery.schedules import crontab
from .models import *


@shared_task(name="order_created")
def order_created(arg):
    """
    Задача для отправки уведомления по электронной почте при успешном создании заказа.
    """
    order_id = arg
    print('hello '+str(order_id))
    order = Post.objects.get(id=order_id)
    subject = 'Order nr. {}'.format(order_id)
    message = 'Dear {},\nYou have successfully placed an order.\nYour order id is {}.'.format(order.title, order.id)

    email = send_mail(subject, message, 'sanja081107@gmail.com', ['alexander_misyuta@mail.ru'])

    return email


@shared_task
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')

    # Calls test('world') every 30 seconds
    sender.add_periodic_task(30.0, test.s('world'), expires=10)
    #
    # Executes every Monday morning at 7:30 a.m.
    sender.add_periodic_task(
        crontab(hour=7, minute=30, day_of_week=1),
        test.s('Happy monday!'),
    )


@shared_task(name="test")
def test(*args):
    return print(args)


@shared_task
def add(x, y):
    z = x + y
    print(z)
