"""Tests for user api endpoint."""

from django.test import TestCase
from django.urls import reverse

from django.contrib.auth import get_user_model

from rest_framework.test import APIClient 
from rest_framework import status


CREATE_USER_URL = reverse('user:create')


def create_user(**params):
    """Create and returns new user."""
    return get_user_model().objects.create(**params)


class PublicApiTests(TestCase):
    """Test for public api."""
    
    def setUp(self):
        self.client = APIClient()
        
    def test_create_new_user(self):
        """Test to create new user."""
        payload = {
            'email': 'abc@example.com',
            'password': 'pass123'
        }
        
        res = self.client.post(CREATE_USER_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        
        user = get_user_model().objects.get(email=payload['email'])
        
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)
        
    def tests_create_user_email_already_exists(self):
        """Test create a new user with email already exists raises error."""
        payload = {
            'email': 'abc@example.com',
            'password': 'pass123'
        }
        create_user(payload)
        
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_user_password_short_error(self):
        """Test the user short password raises error."""
        payload = {
            'email': 'abc@example.com',
            'password': 'pas'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
        user = get_user_model().objects.filter(email=payload['email'])
        self.assertFalse(user.exists())
