"""Tests the Store models
"""

from django.test import TestCase
from store import models

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files import File
from django.db.utils import IntegrityError

import tempfile
from decimal import Decimal
from PIL import Image
import datetime



class StoreModelTests(TestCase):
    """Test cases for store model."""
    def setUp(self):
        self.category1 = models.Category.objects.create(
            name='cat1'
        )
        self.category2 = models.Category.objects.create(
            name='cat2'
        )
    
    def test_category_success(self):
        """test the creation of category success."""
        category_obj = models.Category.objects.all()
        self.assertEqual(category_obj.count(), 2)
        
    def test_category_unique_name(self):
        """Test the unique name of the category."""
        with self.assertRaises(IntegrityError):
            models.Category.objects.create(name='cat1')
            
    def test_category_empty_name_error(self):
        """Test the empty category name raises error."""
        empty_category = models.Category.objects.create(name='')
        self.assertRaises(ValidationError, empty_category.full_clean)
        
    def test_subcategory_success(self):
        """test the creation of category success."""
        subcategory1 = models.SubCategory.objects.create(
            name='subcat1',
            category=self.category1
        )
        subcategory_obj = models.SubCategory.objects.all()
        self.assertEqual(subcategory_obj.count(), 1)
        
    def test_subcategory_unique_name(self):
        """Test the unique name of the category."""
        models.SubCategory.objects.create(
            name='cat1',
            category=self.category1
        )
        
        with self.assertRaises(IntegrityError):
            models.SubCategory.objects.create(
                name='cat1', 
                category=self.category1)
    
    def test_subcategory_empty_name_error(self):
        """Test the empty category name raises error."""
        empty_category = models.SubCategory.objects.create(
            name='', category=self.category1)
        
        self.assertRaises(ValidationError, empty_category.full_clean)
        
    def test_subcategory_unique_name_different_category(self):
        """Test subcategory name uniqueness with different category."""
        models.SubCategory.objects.create(
            name='subcat1',
            category=self.category1
        )
        models.SubCategory.objects.create(
            name='subcat1',
            category=self.category2
        )
        
        self.assertEqual(models.SubCategory.objects.count(), 2)
        

class ProductModelTests(TestCase):
    """Test product model."""
    def setUp(self):
        self.category = models.Category.objects.create(
            name='cat1'
        )
        self.sub_category = models.SubCategory.objects.create(
            name='sub_cat1',
            category=self.category
        )
        self.product = {
            'name': 'Test Product', 
            'description': 'This is a test product.', 
            'price': Decimal('19.99'), 
            'image': SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg')
        }
        
    def tearDown(self):
        """Delete any created instances after each test method."""
        models.Product.objects.all().delete()
        
    def test_create_product_success(self):
        """Test create of product success."""
        
        product = models.Product(
            **self.product,
            sub_category=self.sub_category
        )
        product.full_clean()  
        product.save()
            
        self.assertEqual(models.Product.objects.count(), 1)
        saved_product = models.Product.objects.get(pk=product.pk)
        self.assertEqual(saved_product.name, 'Test Product')
        self.assertEqual(saved_product.description, 'This is a test product.')
        self.assertEqual(saved_product.price, Decimal('19.99'))
        self.assertEqual(saved_product.sub_category, self.sub_category)
        
    def test_product_name_min_length_validation(self):
        """Test the minimum length validation for the name field"""
        self.product['name'] = 'short'
        with self.assertRaises(ValidationError) as context:
            models.Product(
                **self.product, 
                sub_category=self.sub_category
                ).full_clean()
            
        self.assertIn('Product name should have minimum of 8 characters.', str(context.exception))
        
    def test_product_price_min_value_validation(self):
        """Test the minimum value validation for the price field."""
        self.product['price'] = Decimal('0.98')
        with self.assertRaises(ValidationError) as context:
            models.Product(**self.product, 
                           sub_category=self.sub_category,).full_clean()
            
        self.assertIn('Price should be greater than 0.', str(context.exception))

    def test_product_price_max_value_validation(self):
        """Test the maximum value validation for the price field."""
        self.product['price'] = Decimal('1000.00')
        with self.assertRaises(ValidationError) as context:
            models.Product(**self.product, 
                           sub_category=self.sub_category).full_clean()
        self.assertIn('Price should be less than $999.99', str(context.exception))

    def test_product_image_file_extension_validation(self):
        """Test the image file extension validation."""
        self.product['image'] = SimpleUploadedFile(name='test_image.txt', content=b'', content_type='text/plain')
        with self.assertRaises(ValidationError) as context:
            models.Product(**self.product, 
                           sub_category=self.sub_category).full_clean()
        
        self.assertRaisesMessage('Upload a valid image. The file you uploaded was either not an image or a corrupted image.', ValidationError)
        

class InventoryModelTests(TestCase):
    """Tests the Inventory Model."""
    def setUp(self):
        self.category = models.Category.objects.create(
            name='cat1'
        )
        self.sub_category = models.SubCategory.objects.create(
            name='sub_cat1',
            category=self.category
        )
        self.product_instance = {
            'name': 'Test Product', 
            'description': 'This is a test product.', 
            'price': Decimal('19.99'), 
            'image': SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg')
        }
        self.product = models.Product.objects.create(
            **self.product_instance,
            sub_category=self.sub_category)
        
    def tearDown(self):
        """Delete any created instances after each test method."""
        models.Product.objects.all().delete()

    def test_create_inventory_success(self):
        """Test the creation of inventory successfully."""
        models.Inventory.objects.create(
            quantity=10,
            product=self.product
        )
        self.assertEqual(models.Product.objects.count(), 1)
        
    def test_default_inventory(self):
        """Test the empty quantity raises error."""
        inv_default = models.Inventory.objects.create(
            product=self.product
        )
        self.assertEqual(inv_default.quantity, 0)
        
    def test_negative_quantity_inventory_error(self):
        """Test the inventory quantity less than 0 raises error."""
        with self.assertRaises(ValidationError) as context:
            models.Inventory.objects.create(
                quantity=-10,
                product=self.product
            ).full_clean()
        
        self.assertRaisesMessage("Ensure this value is greater than or equal to 0.", ValidationError)
        self.assertIn('quantity', str(context.exception))
        
    def test_greater_than_max_quantity_inventory_error(self):
        """Test the inventory quantity greater than 50 raises error."""
        with self.assertRaises(ValidationError) as context:
            models.Inventory.objects.create(
                quantity=100,
                product=self.product
            ).full_clean()
        
        self.assertRaisesMessage("Ensure this value is less than or equal to 50.", ValidationError)
        self.assertIn('quantity', str(context.exception))
        

class DiscountModelTests(TestCase):
    """Test for model discount."""
    def setUp(self):
        self.category = models.Category.objects.create(
            name='cat1'
        )
        self.sub_category = models.SubCategory.objects.create(
            name='sub_cat1',
            category=self.category
        )
        self.product = models.Product.objects.create(
            name='Test Product', 
            description='This is a test product.', 
            price=Decimal('19.99'), 
            image=SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg'),
            sub_category=self.sub_category
        )
    
    def tearDown(self):
        """Delete any created instances after each test method."""
        models.Product.objects.all().delete()
        
    def test_create_discount_success(self):
        """Test creation of discount for the product."""
        models.Discount.objects.create(
            percent=Decimal(10.99),
            active=True,
            product=self.product
        )
        self.assertEqual(models.Discount.objects.count(), 1)
        
    def test_min_discount_raises_error(self):
        """Tests the minimum discount percent allowed."""
        with self.assertRaises(ValidationError) as context:
            models.Discount.objects.create(
                percent=Decimal(0.02),
                active=True,
                product=self.product
            ).full_clean()
            
        self.assertRaisesMessage("Discount should be minimum of 0.1%%", ValidationError)
        self.assertIn('percent', str(context.exception))
        
    def test_max_discount_raises_error(self):
        """Tests the maximum discount percent allowed."""
        with self.assertRaises(ValidationError) as context:
            models.Discount.objects.create(
                percent=Decimal(99.99),
                active=True,
                product=self.product
            ).full_clean()
            
        self.assertRaisesMessage('Discount should not exceed 99.99%%', ValidationError)
        self.assertRaisesMessage('Ensure that there are no more than 4 digits in total.', ValidationError)
        self.assertIn('percent', str(context.exception))
        
    

        
        
        
    