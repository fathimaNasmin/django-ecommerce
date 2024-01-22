"""Tests for models in User app."""

from django.test import TestCase
from django.contrib.auth import get_user_model


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