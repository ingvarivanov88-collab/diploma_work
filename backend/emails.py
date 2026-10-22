from django.core.mail import send_mail
from django.conf import settings


def send_order_confirmation(user_email, order_id, items):
    """Отправляет клиенту подтверждение заказа."""
    subject = f'Подтверждение заказа #{order_id}'

    message = f'Спасибо за ваш заказ #{order_id}!\n\n'
    message += 'Ваш заказ:\n'
    for item in items:
        message += f'- {item.product.name} (x{item.quantity})\n'

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )


def send_invoice_to_admin(order_id, items, user):
    """Отправляет накладную администратору."""
    subject = f'Новая накладная по заказу #{order_id}'

    message = f'Поступил новый заказ #{order_id} от {user.username}.\n\n'
    message += 'Состав заказа:\n'
    for item in items:
        message += f'- {item.product.name} (x{item.quantity}) — {item.product.price} руб.\n'

    admin_email = 'admin@diploma_work.ru'

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [admin_email],
        fail_silently=False,
    )


def send_status_update(user_email, order_id, new_status):
    """Отправляет клиенту уведомление о смене статуса заказа."""
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