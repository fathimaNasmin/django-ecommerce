"""Tests for store api end points."""

import tempfile
from decimal import Decimal
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient

from store.models import (
    Category, 
    SubCategory, 
    Product,
    Inventory,
    Discount
)

from store.serializers import (
    CategorySerializer, 
    SubCategorySerializer, 
    ProductSerializer
    )


CATEGORY_URL = reverse('store:category-list')
SUB_CATEGORY_URL = reverse('store:sub-category-list')
PRODUCT_URL = reverse('store:product-list')


def create_test_image():
    """Function to create image for testing."""
    with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
        img = Image.new('RGB', (10, 10))
        img.save(image_file, format='JPEG')
        image_file.seek(0)
        
        uploaded_file = SimpleUploadedFile(
            name='test_image.jpg',
            content=image_file.read(),
            content_type='image/jpeg'
        )
    return uploaded_file


def create_category(name='category1'):
    """A function to create a category."""
    return Category.objects.create(name=name)


def create_sub_category(category, name='subcategory1'):
    """Method function to create subcategory."""
    return SubCategory.objects.create(
        name=name,
        category=category
    )

   
def create_product(name, price, image, description, sub_category):
    """Create and returns product."""
    return Product.objects.create(
        name=name,
        price=price,
        image=image,
        description=description,
        sub_category=sub_category
    )


def create_inventory(product):
    """Create and returns inventory."""
    return Inventory.objects.create(
        product=product
    )


def create_discount(percent, product):
    """Create and return discount."""
    valid_till = timezone.now() + timezone.timedelta(days=30)
    return Discount.objects.create(
        percent=Decimal(percent),
        active=True,
        valid_till=valid_till,
        product=product
    )


class PublicAPITests(TestCase):
    """Test the endpoints for unauthenticated users."""
    def setUp(self):
        self.client = APIClient()
        
    def test_get_category(self):
        """test listing category api."""
        create_category('category1')
        create_category('category2')
        
        res = self.client.get(CATEGORY_URL)
        
        categories = Category.objects.all().order_by('id')
        serializer = CategorySerializer(categories, many=True)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        
    def test_get_sub_category(self):
        """Test listing subcategory."""
        cat1 = create_category('cat1')
        cat2 = create_category('cat2')
        create_sub_category(name='subcat1', category=cat1)
        create_sub_category(name='subcat2', category=cat2)
        
        res = self.client.get(SUB_CATEGORY_URL)
        
        subcategories = SubCategory.objects.all().order_by('id')
        serializer = SubCategorySerializer(subcategories, many=True)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        
    def test_get_products(self):
        """Test listing all products."""
        test_image = create_test_image()
        cat1 = create_category('cat1')
        sub_1 = create_sub_category(name='subcat1', category=cat1)
        create_sub_category(name='subcat2', category=cat1)
        self.product = create_product(
            name='product1',
            price=Decimal('10.99'),
            image=test_image,
            description='description for product 1',
            sub_category=sub_1
        )
        create_inventory(self.product)
        create_discount(percent=3.00, product=self.product)
        
        res = self.client.get(PRODUCT_URL)
        
        product = Product.objects.all().order_by('id')
        discount = Discount.objects.get(product=self.product.id)
        serializer = ProductSerializer(product, many=True)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['name'], serializer.data[0]['name'])
        self.assertEqual(res.data[0]['product_inventory'], 
                         serializer.data[0]['product_inventory'])
        self.assertEqual(res.data[0]['discount'], 
                         serializer.data[0]['discount'])
        self.assertEqual(res.data[0]['discount'][0]['percent'], 
                         str(discount.percent))
        