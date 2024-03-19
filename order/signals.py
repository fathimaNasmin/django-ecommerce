"""Signals for order."""
from django.conf import settings

from django.core.mail import send_mail, EmailMultiAlternatives
from email.utils import formataddr

from django.template.loader import render_to_string

from django.db.models.signals import post_save
from django.dispatch import receiver

from order.models import Order


@receiver(post_save, sender=Order)
def order_created(sender, instance, created, **kwargs):
    """
    Signals triggers when order is saved.
    """
    if created:
        # send mail to the customer.
        sender_name = "E-commerce"
        sender_email = settings.EMAIL_HOST_USER
        from_email = formataddr((sender_name, sender_email))

        subject, to = "Order confirmation", instance.email
        html_message = render_to_string(
            'order/templates/confirmation_mail.html',
            {'customer_name': instance.customer.full_name,
             'order_id': instance.order_id,
             'all_products': instance.orderdetail_set.all(),
             'total_amount': instance.amount})
        plain_message = "Order Confirmation"
        msg = EmailMultiAlternatives(subject, plain_message, from_email, [to])
        msg.attach_alternative(html_message, "text/html")
        msg.send()
        pass
