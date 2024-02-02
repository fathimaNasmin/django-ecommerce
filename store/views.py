"""views for store endpoints
"""
from store.models import Category, SubCategory, Product, Inventory
from store.serializers import (CategorySerializer,
                               SubCategorySerializer,
                               ProductSerializer)

from rest_framework import permissions, viewsets, status
from rest_framework.response import Response

from django.db.models import Prefetch

from store.permissions import AdminOnlyPermission


class CategoryViewSet(viewsets.ModelViewSet):
    """View to lists all Category."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AdminOnlyPermission]


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
