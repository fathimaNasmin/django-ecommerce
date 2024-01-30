from django.contrib import admin

from order.models import Order, OrderDetail

admin.site.register(Order)
admin.site.register(OrderDetail)
