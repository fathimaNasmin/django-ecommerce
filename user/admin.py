"""Django admin customization."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin 
from django.utils.translation import gettext_lazy as _ 

from user import models


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
            'classes': ('wide',),
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


admin.site.register(models.User, UserAdmin)

