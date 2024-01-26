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
        

class Inventory(models.Model):
    """Inventory of the product."""
    quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    
class Discount(models.Model):
    """Discount of the product."""
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    percent = models.DecimalField(max_digits=4, decimal_places=2,
                                  validators=[
                                    validators.MinValueValidator(
                                        limit_value=0.1, 
                                        message='Discount should be minimum of 0.1%'
                                        ), 
                                    validators.MaxValueValidator(
                                        limit_value=99.99,
                                        message='Discount should not exceed 99.99%'
                                        )
                                    ])
    
    active = models.BooleanField(default=False, verbose_name='Is on sale')
    
    
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
    discount = models.ForeignKey(Discount, null=True, blank=True, on_delete=models.CASCADE)
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    


    
    
    