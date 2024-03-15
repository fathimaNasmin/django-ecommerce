"""Task scheduling for celery."""

from celery import shared_task

from django.conf import settings

from django.core.mail import EmailMultiAlternatives
from email.utils import formataddr

from django.template.loader import render_to_string

from order.models import Order


@shared_task(bind=True)
def send_order_confirmation_mail(self, order_id):
    customer_order = Order.objects.get(id=order_id)
    # Mail body
    sender_name = "E-commerce"
    sender_email = settings.EMAIL_HOST_USER
    from_email = formataddr((sender_name, sender_email))

    subject, to = "Order confirmation", customer_order.customer.email
    html_message = render_to_string(
        'order/templates/confirmation_mail.html',
        {'customer_name': customer_order.customer.full_name,
            'order_id': customer_order.order_id,
            'all_products': customer_order.orderdetail_set.all(),
            'total_amount': customer_order.amount})
    plain_message = "Order Confirmation"
    msg = EmailMultiAlternatives(subject, plain_message, from_email, [to])
    msg.attach_alternative(html_message, "text/html")
    msg.send()
    return "Done mailing"