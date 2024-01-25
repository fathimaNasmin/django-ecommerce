"""Store Models.
"""
from django.db import models

from django.core import validators


# Custom model Validation

class Category(models.Model):
    """Category model for products."""
    name = models.CharField(max_length=255, unique=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return f'Category-{self.name}'
    
    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super().save(*args, **kwargs)
    
       
class SubCategory(models.Model):
    """Sub Category model for products."""
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Sub Category'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'category'],
                name='unique_category')
        ]
    
    def __str__(self):
        return f'Sub Category-{self.name}'
      
    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super().save(*args, **kwargs)
        

class Product(models.Model):
    """Product model."""
    name = models.CharField(max_length=255, 
                            validators=[
                                validators.MinLengthValidator(
                                    limit_value=8,
                                    message='Product name should have minimum of 8 characters.')
                                ]
                            )
    description = models.TextField()
    price = models.DecimalField(max_digits=5, 
                                decimal_places=2,
                                validators=[validators.MinValueValidator(
                                    limit_value=0.99, 
                                    message='Price should be greater than 0.'),
                                            validators.MaxValueValidator(
                                                limit_value=999.99,
                                                message='Price should be less than $999.99'
                                            )
                                    ]
                                )
    image = models.ImageField(upload_to='products/images/',
                              validators=[
                                  validators.validate_image_file_extension
                                  ])
    created_at = models.DateField(auto_now_add=True)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    # discount_id