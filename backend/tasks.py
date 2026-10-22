from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_order_confirmation_task(user_email, order_id, items):
    """Фоновая задача: отправка подтверждения заказа клиенту."""
    subject = f'Подтверждение заказа #{order_id}'

    message = f'Спасибо за ваш заказ #{order_id}!\n\n'
    message += 'Ваш заказ:\n'
    for item in items:
        message += f'- {item["product"]} (x{item["quantity"]})\n'

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )


@shared_task
def send_invoice_to_admin_task(order_id, items, username):
    """Фоновая задача: отправка накладной администратору."""
    subject = f'Новая накладная по заказу #{order_id}'

    message = f'Поступил новый заказ #{order_id} от {username}.\n\n'
    message += 'Состав заказа:\n'
    for item in items:
        message += f'- {item["product"]} (x{item["quantity"]}) — {item["price"]} руб.\n'

    admin_email = 'admin@diploma_work.ru'

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [admin_email],
        fail_silently=False,
    )


@shared_task
def send_status_update_task(user_email, order_id, new_status):
    """Фоновая задача: уведомление о смене статуса."""
    subject = f'Статус вашего заказа #{order_id} изменён'

    message = f'Статус вашего заказа #{order_id} был изменён на: {new_status}.\n'
    message += 'Спасибо, что выбрали нас!'

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )