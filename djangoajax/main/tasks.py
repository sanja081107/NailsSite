from celery import shared_task
from django.core.mail import send_mail
from .models import *

@shared_task
def order_created(order_id):
    """
    Задача для отправки уведомления по электронной почте при успешном создании заказа.
    """
    order = Post.objects.get(id=order_id)
    subject = 'Order nr. {}'.format(order_id)
    message = 'Dear {},\n\nYou have successfully placed an order.\
                Your order id is {}.'.format(order.title,
                                             order.id)
    mail_sent = send_mail(subject,
                          message,
                          'sanja081107@gmail.com',
                          ['alexander_misyuta@mail.ru'])
    return mail_sent
