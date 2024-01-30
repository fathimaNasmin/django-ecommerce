from django.contrib import admin
from store.models import (
    Product,
    Category,
    SubCategory,
    Inventory, 
    Discount)

admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Product)
admin.site.register(Inventory)
admin.site.register(Discount)
