"""views for store endpoints
"""
from store.models import Category, SubCategory, Product, Inventory
from store.serializers import (CategorySerializer,
                               SubCategorySerializer,
                               ProductSerializer,
                               ProductImageSerializer)

from rest_framework import permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.mixins import (ListModelMixin,
                                   RetrieveModelMixin,
                                   CreateModelMixin,
                                   UpdateModelMixin,
                                   DestroyModelMixin)


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
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    permission_classes = [AdminOnlyPermission]


class ProductViewSet(viewsets.ModelViewSet):
    """A simple viewset for listing and retrieving products."""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AdminOnlyPermission]

    def get_serializer_class(self):
        """Return the serializer class for the request."""
        if self.action == 'upload_image':
            return ProductImageSerializer

        return self.serializer_class

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save()

    # Custom action for uploading image for product.
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to product."""
        product = self.get_object()
        serializer = self.get_serializer(product, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
