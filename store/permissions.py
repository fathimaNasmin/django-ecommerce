from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS


class AdminOnlyPermission(BasePermission):
    """Custom permission for admin users."""
    admin_methods = ('POST', 'PUT', 'PATCH', 'DELETE')
    
    def has_permission(self, request, view):
        if (request.user.is_staff and 
            request.user.is_superuser and
            request.method in self.admin_methods):
            return True 
        elif request.method in SAFE_METHODS:
            return True
        return False
        
    def has_object_permission(self, request, view, obj):
        if (request.user.is_staff and 
            request.user.is_superuser and
            request.method in self.admin_methods):
            return True 
        elif request.method in SAFE_METHODS:
            return True
        return False
        