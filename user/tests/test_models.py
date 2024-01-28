"""Tests for models in User app."""
from decimal import Decimal

from django.test import TestCase

from django.contrib.auth import get_user_model
from user import models as user_model
from store import models as store_model

from django.core.exceptions import ValidationError
from django.db import IntegrityError


class ModelTests(TestCase):
    """Test User models."""
    
    def test_create_user_email_sucessfull(self):
        """Create a user with email successfull."""
        email = 'test@example.com'
        password = 'testpassword'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        
    def test_new_email_normalized(self):
        """Test the new email id is normalized."""
        sample_emails = [
            ['test1@EXAMPLE.COM', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@Example.com', 'TEST3@example.com'],
            ['test4@example.com', 'test4@example.com']
        ]
        
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)
            
    def test_user_without_email_raises_error(self):
        """Test the user without email raises a value error."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'testpassword')
            
    def test_create_superuser(self):
        """Test creating superuser."""
        user = get_user_model().objects.create_superuser(
            email='test@example.com',
            password='testpass'
        )
        
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        
        
class ShippingAddressModelTests(TestCase):
    """Tests the shipping address model."""
    def setUp(self):
        self.user = get_user_model().objects.create(
            email='test@example.com',
            password='testpass'
        )
        self.address = models.ShippingAddress.objects.create(
            street='3000 swallow hill rd',
            building='111',
            city='new jersey city',
            state='NJ',
            zipcode='12344',
            customer=self.user
        )
        
    def test_create_user_address(self):
        """Test creating user address."""
        self.assertEqual(self.address.street, '3000 swallow hill rd')
        self.assertEqual(self.address.customer, self.user)
        self.assertEqual(len(self.address.zipcode), 5)
        
    def test_address_zipcode_raises_error(self):
        """Test the address zipcode validation error."""
        invalid_zipcode = models.ShippingAddress.objects.create(
            street='3000 swallow hill rd',
            building='111',
            city='new jersey city',
            state='NJ',
            zipcode='1234433',
            customer=self.user
        )
        self.assertRaises(ValidationError, invalid_zipcode.full_clean)
        
    def test_empty_address_error(self):
        """Test empty address raises error."""
        empty_address = models.ShippingAddress.objects.create(
            street='',
            building=None,
            city='',
            state='',
            zipcode=12345,
            customer=self.user
        )
        with self.assertRaises(ValidationError):
            empty_address.full_clean()


class CartItemModelTests(TestCase):
    """Tests the CartItem Model."""
    def setUp(self):
        self.category = store_model.Category.objects.create(name='home_decor')
        self.sub_category = store_model.SubCategory.objects.create(
            name='wall decor', 
            category=self.category)
        self.product = store_model.Product.objects.create(
            name='xyz',
            description='xyz description',
            price=Decimal('10.98'),
            sub_category=self.sub_category
            )
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='password12344'
        )
        
    def test_create_cart_item(self):
        """Test the creation of cart item."""
        cartItem1 = user_model.CartItem.objects.create(
            product=self.product,
            user=self.user,
            quantity=1
        )    
        
        self.assertEqual(user_model.CartItem.objects.count(), 1)
        self.assertEqual(cartItem1.product.name, 'xyz')
        
    def test_cartItem_min_value(self):
        """Test the minimum quantity of the cart item."""
        cartItem1 = user_model.CartItem.objects.create(
            product=self.product,
            user=self.user,
            quantity=0
        )
        
        with self.assertRaises(ValidationError):
            cartItem1.full_clean()
            
    def test_user_cart_has_multiple_product(self):
        """Test the user cart has multiple items"""
        cartItem1 = user_model.CartItem.objects.create(
            product=self.product,
            user=self.user,
            quantity=1
        )
        product2 = store_model.Product.objects.create(
            name='product2',
            description='product2 description',
            price=Decimal('99.98'),
            sub_category=self.sub_category
            )
        cartItem2 = user_model.CartItem.objects.create(
            product=product2,
            user=self.user,
            quantity=1
        )
        
        cart_items = user_model.CartItem.objects.all()
        self.assertEqual(cart_items.count(), 2)
        
        self.assertEqual(cartItem1.product.name, 'xyz')
        self.assertEqual(cartItem2.product.name, 'product2')