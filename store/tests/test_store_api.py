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

from django.contrib.auth import get_user_model
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


def sub_category_detail_url(id):
    """create and return subcategory detail url."""
    return reverse('store:sub-category-detail', args=[id])

def category_detail_url(id):
    """create and return category detail url."""
    return reverse('store:category-detail', args=[id])


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
        self.normal_user = get_user_model().objects.create_user(
            email='normaluser@example.com',
            password='user@1234'
        )

    def test_get_category(self):
        """test listing category api."""
        create_category('category1')
        create_category('category2')

        res = self.client.get(CATEGORY_URL)

        categories = Category.objects.all().order_by('id')
        serializer = CategorySerializer(categories, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_category_no_user_raises_error(self):
        """Test create category by anonymous user."""
        payload = {
            'name': 'games'
        }
        res = self.client.post(CATEGORY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_category_normal_user_error(self):
        """Test create category raises error for normal users."""
        self.client.force_authenticate(self.normal_user)

        payload = {
            'name': 'toys'
        }
        res = self.client.post(CATEGORY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

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


class AdminAPITests(TestCase):
    """Test Admin api end points."""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='admin123455'
        )
        self.client.force_authenticate(self.admin_user)

    def test_get_category_admin_user(self):
        """Test get category for admin user."""
        create_category('categor1')
        create_category('categor2')

        res = self.client.get(CATEGORY_URL)

        categories = Category.objects.all().order_by('id')
        serializer = CategorySerializer(categories, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_category_admin_user(self):
        """Test create category only by admin user."""
        payload = {
            'name': 'toys'
        }
        res = self.client.post(CATEGORY_URL, payload)

        category = Category.objects.get(name=payload['name'])
        serializer = CategorySerializer(category)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data, serializer.data)
        
    def test_new_category_with_new_subcategories(self):
        """Test posting new category with new subcategories."""
        payload = {
            'name': 'new_cat',
            'sub_category': [
                {'name': 'new sub category'}
            ]
        }
        
        res = self.client.post(CATEGORY_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_patch_category_admin_user(self):
        """Test editing the category name by the admin user."""
        clothing = create_category(name='clothing')

        payload = {'name': 'fashion'}
        url = category_detail_url(clothing.id)

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        clothing.refresh_from_db()
        self.assertEqual(clothing.name, payload['name'])

    def test_delete_category_admin_user(self):
        """Test deleting the category by the admin user."""
        clothing = create_category(name='clothing')

        url = category_detail_url(clothing.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        clothing_exists = Category.objects.filter(name='clothing').exists()
        self.assertFalse(clothing_exists)

    def test_get_category_detail_admin_user(self):
        """Test get category detail for admin user."""
        arts = create_category(name='arts')
        url = category_detail_url(arts.id)

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = CategorySerializer(arts)
        self.assertEqual(res.data, serializer.data)

    def test_post_sub_category_to_existing_category(self):
        """Test posting sub category to existing category."""
        self.client.force_authenticate(self.admin_user)

        test_category = create_category(name='testcategory')

        payload = {
            'name': 'test_sub_cat',
            'category': test_category.id
        }
        res = self.client.post(SUB_CATEGORY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        test_sub_category = SubCategory.objects.get(category=test_category)
        serializer = SubCategorySerializer(test_sub_category)
        self.assertEqual(res.data, serializer.data)
        
    def test_patch_sub_category(self):
        """Test update sub category."""
        cat_test1 = create_category(name='test_cat1')
        sub_cat = create_sub_category(
            name='sub_cat1',
            category=cat_test1
        )
        
        payload = {
            'name': 'update_sub_cat',
            'category': cat_test1.id
        }
        
        url = sub_category_detail_url(sub_cat.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
        obj = SubCategory.objects.get(name=payload['name'])
        serializer = SubCategorySerializer(obj)
        
        self.assertEqual(res.data, serializer.data)
        
    def test_delete_sub_category(self):
        """Test delete sub category."""
        cat_test1 = create_category(name='test_cat1')
        sub_cat = create_sub_category(
            name='sub_cat1',
            category=cat_test1
        )

        url = sub_category_detail_url(sub_cat.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
