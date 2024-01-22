"""User models
"""

from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, 
                                        BaseUserManager, 
                                        PermissionsMixin)


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
    
