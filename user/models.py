"""User models
"""

from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, 
                                        BaseUserManager, 
                                        PermissionsMixin)
from django.core.exceptions import ValidationError

from store.models import Product

from django.core import validators


# Custom Model Validation 
def validate_zipcode(zipcode):
    """Custom function for validating the zipcode of the user address."""
    if zipcode > 0 and len(str(abs(zipcode))) == 5:
        return zipcode
    else:
        raise ValidationError("Enter an valid zipcode")    


class UserManager(BaseUserManager):
    """Manage for user."""
    def create_user(self, email, password=None, **extra_field):
        """create, save and return user."""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_field)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """Create,save and return super user."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
        

class User(AbstractBaseUser, PermissionsMixin):
    """User custom model."""
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    
    def __str__(self):
        return f"{self.email}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    

class ShippingAddress(models.Model):
    """Shipping Address of the user."""
    street = models.CharField(max_length=255)
    building = models.IntegerField(null=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zipcode = models.IntegerField(validators=[validate_zipcode])
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.customer.full_name} - {self.city},{self.state}"
    
    class Meta:
        verbose_name_plural = 'Shipping Address'
        
        
class CartItem(models.Model):
    """Cart of the user."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1, 
                                   validators=[validators.MinValueValidator(
                                       limit_value=1)])
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"CartItem of {self.user.name}"    

    def total_cart_amount(self):
        """Returns the total amount of the cartitems """
        return self.quantity * self.product.price