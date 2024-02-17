"""Tests for user api endpoint."""

from django.test import TestCase
from django.urls import reverse

from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:register')
TOKEN_URL = reverse('user:token')
PROFILE_URL = reverse('user:profile')


def create_user(**params):
    """Create and returns new user."""
    return get_user_model().objects.create_user(**params)


class PublicApiTests(TestCase):
    """Test for public api."""

    def setUp(self):
        self.client = APIClient()

    def test_create_new_user(self):
        """Test to create new user."""
        payload = {
            'email': 'abc@example.com',
            'password': 'pass12345$'
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
        create_user(**payload)

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

    def test_create_token_user(self):
        """Test token for valid credentials."""
        user_details = {
            'email': 'test123@example.com',
            'password': 'dhjhdi&%*^%$IUhsg'
        }
        create_user(**user_details)

        payload = {
            'email': 'test123@example.com',
            'password': 'dhjhdi&%*^%$IUhsg'
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_user_invalid_credentials(self):
        """Test no token on invalid credentials."""
        user_details = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        create_user(**user_details)

        payload = {
            'email': 'invalid@example.com',
            'password': 'passfhjgkdf'
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_blank_password(self):
        """Test posting with blank password raises error"""

        payload = {
            'email': 'invalid@example.com',
            'password': ''
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test authentication required."""
        res = self.client.get(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAPITests(TestCase):
    """Test for private api."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example.com',
            password='testpass1234'
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user_profile_success(self):
        """Test retrieve user."""
        res = self.client.get(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {'email': self.user.email})

    def test_user_profile_post_not_allowed(self):
        """Test post on user profile not allowed."""
        res = self.client.post(PROFILE_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test update user profile."""
        payload = {
            'first_name': 'Test 1',
            'last_name': 'Lastname',
            'password': 'updatedpassword'
        }

        res = self.client.patch(PROFILE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()

        self.assertEqual(self.user.first_name, payload['first_name'])
        self.assertEqual(self.user.last_name, payload['last_name'])
        self.assertTrue(self.user.check_password(payload['password']))
