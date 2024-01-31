"""views for store endpoints
"""
from store.models import Category, SubCategory, Product, Inventory
from store.serializers import (CategorySerializer,
                               SubCategorySerializer,
                               ProductSerializer)

from rest_framework import permissions, viewsets

from django.db.models import Prefetch

# /category/ :GET
# /category/<cateory_id>/ : view detail

class CategoryViewSet(viewsets.ModelViewSet):
    """View to lists all Category."""
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class SubCategoryViewSet(viewsets.ModelViewSet):
    """View to lists all subcategory."""
    queryset = SubCategory.objects.all().order_by('id')
    serializer_class = SubCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ProductViewSet(viewsets.ModelViewSet):
    """View to lists all products."""
    queryset = Product.objects.all().order_by('id')[:5]
    # queryset = Product.objects.prefetch_related('inventory_set').order_by('id')[:5]
    # queryset = Product.objects.select_related('inventory').order_by('id')[:5]
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    