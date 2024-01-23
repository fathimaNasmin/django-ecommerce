"""Tests for models in User app."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from user import models

from django.core.exceptions import ValidationError


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
            self.assertRaises(ValidationError, self.address.full_clean)
            
        def test_empty_address_error(self):
            """Test empty address raises error."""
            empty_address = models.ShippingAddress.objects.create(
                street='',
                building='',
                city='',
                state='',
                zipcode='',
                customer=self.user
            )
            self.assertRaises(ValidationError, empty_address.full_clean)
