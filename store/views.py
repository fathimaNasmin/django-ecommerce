"""views for store endpoints
"""
from store.models import Category, SubCategory, Product, Inventory
from store.serializers import (CategorySerializer,
                               SubCategorySerializer,
                               ProductSerializer)

from rest_framework import permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from django.db.models import Prefetch

from store.permissions import AdminOnlyPermission


class CategoryViewSet(viewsets.ModelViewSet):
    """View to lists all Category."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AdminOnlyPermission]

    def create(self, request, *args, **kwargs):
        # You can access request.data directly in the serializer
        serializer = self.get_serializer(data=request.data)

        # The serializer is automatically validated when accessing .data
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Handle the case where validation fails
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        # Additional logic if needed when creating the object
        serializer.save()


class SubCategoryViewSet(viewsets.ModelViewSet):
    """View to lists all subcategory."""
    queryset = SubCategory.objects.all().order_by('id')
    serializer_class = SubCategorySerializer
    permission_classes = [AdminOnlyPermission]
    
class ProductViewSet(viewsets.ModelViewSet):
    """View to lists all products."""
    queryset = Product.objects.all().order_by('id')[:5]
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
