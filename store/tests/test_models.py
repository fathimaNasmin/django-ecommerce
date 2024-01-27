"""Tests the Store models
"""
from django.test import override_settings
import shutil
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


# SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg')
TEST_DIR = 'test_data'


def create_a_product(p_name, p_desc, p_price, subcategory):
    """A helper function to create and return a product."""
    return models.Product.objects.create(
            name=p_name, 
            description=p_desc, 
            price=Decimal(p_price),
            sub_category=subcategory
    )
    

def create_a_sub_category(sub_category, category):
    """A helper function to create and returns sub_category objects."""
    return models.SubCategory.objects.create(
        name=sub_category,
        category=category
    )


def create_a_category(category_name):
    """A helper function to create and returns category object."""
    return models.Category.objects.create(
        name=category_name
    )


class StoreModelTests(TestCase):
    """Test cases for store model."""
    def setUp(self):
        self.category1 = create_a_category('cat1')
        self.category2 = create_a_category('cat2')
    
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
        empty_category = create_a_category('')
        self.assertRaises(ValidationError, empty_category.full_clean)
        
    def test_subcategory_success(self):
        """test the creation of category success."""
        subcategory1 = create_a_sub_category('subcat1', self.category1)
        subcategory_obj = models.SubCategory.objects.all()
        self.assertEqual(subcategory_obj.count(), 1)
        self.assertEqual(subcategory1.name, 'subcat1')
        
    def test_subcategory_unique_name(self):
        """Test the unique name of the category."""
        create_a_sub_category('subcat1', self.category1)
        
        with self.assertRaises(IntegrityError):
            models.SubCategory.objects.create(
                name='subcat1', 
                category=self.category1)
    
    def test_subcategory_empty_name_error(self):
        """Test the empty category name raises error."""
        empty_category = create_a_sub_category('', self.category1)
        
        self.assertRaises(ValidationError, empty_category.full_clean)
        
    def test_subcategory_unique_name_different_category(self):
        """Test subcategory name uniqueness with different category."""
        create_a_sub_category('subcat1', self.category1)
        create_a_sub_category('subcat1', self.category2)
        
        self.assertEqual(models.SubCategory.objects.count(), 2)
        

class ProductModelTests(TestCase):
    """Test product model."""
    def test_create_product_success(self):
        """Test create of product success."""
        self.category = create_a_category('home decor')
        self.sub_category = create_a_sub_category('wall decor', self.category)
        self.product = create_a_product('xyz mirror',
                                        'xyz description',
                                        '69.99',
                                        self.sub_category
                                        )
        # product = models.Product(
        #     **self.product,
        #     sub_category=self.sub_category
        # )
        # product.full_clean()  
        # product.save()
            
        self.assertEqual(models.Product.objects.count(), 1)
        saved_product = models.Product.objects.get(pk=self.product.pk)
        self.assertEqual(saved_product.name, 'xyz mirror')
        self.assertEqual(saved_product.description, 'xyz description')
        self.assertEqual(saved_product.price, Decimal('69.99'))
        self.assertEqual(saved_product.sub_category, self.sub_category)
    
    def test_product_name_min_length_validation(self):
        """Test the minimum length validation for the name field"""
        self.category = create_a_category('home decor')
        self.sub_category = create_a_sub_category('wall decor', self.category)
        self.product = create_a_product('xyz',
                                        'xyz description',
                                        '69.99',
                                        self.sub_category
                                        )
        # self.product['name'] = 'short'
        with self.assertRaises(ValidationError) as context:
            self.product.full_clean()
            
        self.assertIn('Product name should have minimum of 8 characters.', 
                      str(context.exception))
    
    def test_product_price_min_value_validation(self):
        """Test the minimum value validation for the price field."""
        self.category = create_a_category('home decor')
        self.sub_category = create_a_sub_category('wall decor', self.category)
        self.product = create_a_product('xyz',
                                        'xyz description',
                                        '0.98',
                                        self.sub_category
                                        )
        # self.product['price'] = Decimal('0.98')
        with self.assertRaises(ValidationError) as context:
            self.product.full_clean()
            
        self.assertIn('Price should be greater than 0.', 
                      str(context.exception))

          
class ProductImageUploadTests(TestCase):
    """Tests the image uploads."""
    def setUp(self):
        self.category = create_a_category('home decor')
        self.sub_category = create_a_sub_category('wall decor', self.category)
        self.product = models.Product.objects.create(
            name='xyz',
            description='xyz description',
            price=Decimal('10.98'),
            sub_category=self.sub_category
            )
        
    def tearDown(self):
        self.product.image.delete()
        self.product.delete()
        
    def test_upload_image(self):
        """Test the image upload."""
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            
            uploaded_file = SimpleUploadedFile(
                name='test_image.jpg',
                content=image_file.read(),
                content_type='image/jpeg'
            )
            
            self.product.image = uploaded_file
            self.product.save()
            
        self.assertTrue(self.product.image)
        self.assertTrue(self.product.image.name.endswith('.jpg'))
            
            
class InventoryModelTests(TestCase):
    """Tests the Inventory Model."""
    def setUp(self):
        self.category = create_a_category('home decor')
        self.sub_category = create_a_sub_category('wall decor', self.category)
        self.product = models.Product.objects.create(
            name='xyz',
            description='xyz description',
            price=Decimal('10.98'),
            sub_category=self.sub_category
            )
        
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
        
    

        
        
        
    