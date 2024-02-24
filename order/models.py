"""Models for Orders.
"""

from django.db import models
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils import timezone

import uuid

from user.models import User
from store.models import Product


# Custom validation function.
def validate_quantity(quantity):
    """Function validates the amount field in order."""
    if quantity < 1:
        raise ValidationError('Minimum quantity is 1.')


def validate_amount(value):
    """Function validates the amount field in order."""
    if value <= 0:
        raise ValidationError('Amount should be greater than 0.')


class Payment(models.Model):
    """Store transaction id for success payments."""
    transaction_id = models.CharField(max_length=255)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    order_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    is_successful = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)


class Order(models.Model):
    """Stores orders of the customer."""
    order_id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2,
                                 validators=[validate_amount])
    order_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=255)
    
    class Meta:
        ordering = ['-order_date']
    
    def __str__(self):
        return f"{self.order_id} - {self.customer.full_name}"   
            
    
class OrderDetail(models.Model):
    """Stores the orders details in each order."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[validate_quantity])
    
    price = models.DecimalField(max_digits=5, decimal_places=2)
    
    def __str__(self):
        return f"{self.order.order_id}"
    
    
    


