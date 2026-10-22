from django.core.mail import send_mail
from django.conf import settings


def send_order_confirmation(user_email, order_id, items):
    """Отправляет клиенту подтверждение заказа."""
    subject = f'Подтверждение заказа #{order_id}'

    # Формируем текст письма
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

    # Формируем текст накладной
    message = f'Поступил новый заказ #{order_id} от {user.username}.\n\n'
    message += 'Состав заказа:\n'
    for item in items:
        message += f'- {item.product.name} (x{item.quantity}) — {item.product.price} руб.\n'

    # В реальном проекте email админа берется из настроек или модели
    admin_email = 'admin@diploma_work.ru'

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [admin_email],
        fail_silently=False,
    )