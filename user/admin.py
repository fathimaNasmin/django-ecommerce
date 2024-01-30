"""Django admin customization."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin 
from django.utils.translation import gettext_lazy as _ 

from user import models
from order.models import Order


class UserOrders(admin.TabularInline):
    model = Order
    extra = 0
    readonly_fields = ('order_id', 'order_date', 'amount')
   
    
class ShippingAddressInline(admin.TabularInline):
    """
    Tabular Inline in useradmin for showing the 
    addresses of the particular user.
    """
    model = models.ShippingAddress
    extra = 0
    readonly_fields = ('street', 'building', 'city', 'state', 'zipcode')


class UserAdmin(BaseUserAdmin):
    """Define admin page for user."""
    ordering = ['-id']
    list_display = ['email', 'first_name', 'created_at']
    fieldsets = (
        (None, {'fields': ('email', 'password',)}),
        (
            _('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',)}
        ),
        (_('Important dates'), {'fields': ('created_at',)})
    )
    readonly_fields = ['created_at']
    add_fieldsets = (
        (None, {
            'classes': ["wide", "extrapretty"],
            'fields': (
                'email',
                'password1',
                'password2',
                'first_name',
                'last_name',
                'is_active',
                'is_staff',
                'is_superuser',
            )
        }),
    )
    list_filter = ('created_at',)
    inlines = [ShippingAddressInline, UserOrders]


class ShippingAddressAdmin(admin.ModelAdmin):
    """Define shipping address in User."""
    list_display = ('street', 'city', 'state', 'zipcode', 'customer_email')
    list_filter = ('state',)
    search_fields = ('state', 'city', 'zipcode',)

    def customer_email(self, obj):
        return obj.customer.email

    customer_email.short_description = 'Customer Email'
    

admin.site.register(models.User, UserAdmin)
admin.site.register(models.ShippingAddress, ShippingAddressAdmin)

