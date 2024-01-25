"""Store Models.
"""
from django.db import models


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
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    image = models.ImageField(upload_to='products/images/')
    created_at = models.DateField(auto_now_add=True)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    # discount_id