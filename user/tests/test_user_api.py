"""Tests for user api endpoint."""

from django.test import TestCase
from django.urls import reverse

from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from user.serializers import AddressSerializer
from user.models import ShippingAddress

CREATE_USER_URL = reverse('user:register')
TOKEN_URL = reverse('user:token')
PROFILE_URL = reverse('user:profile')
ADDRESS_URL = reverse('user:address-list')


def address_detail_url(address_id):
    """Create and return detail url for address."""
    return reverse('user:address-detail', args=[address_id])


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
            'password': 'pass12345$',
            'first_name': 'firstname',
            'last_name': 'Lastname'
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
            'password': 'pass123',
            'first_name': 'firstname',
            'last_name': 'Lastname'
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
            'password': 'dhjhdi&%*^%$IUhsg',
            'first_name': 'firstname',
            'last_name': 'Lastname'
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
            'password': 'testpass123',
            'first_name': 'firstname',
            'last_name': 'Lastname'
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

    def test_retrieve_address_user_unauthorized(self):
        """Test retrieve address of user for unauthorized user."""
        res = self.client.get(ADDRESS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_access(self):
        payload = {
            'street': '3000 swallow hill rd',
            'building': '112',
            'city': 'pittsburgh',
            'state': 'PA',
            'zipcode': 15220
        }
        response = self.client.post(ADDRESS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAPITests(TestCase):
    """Test for private api."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example.com',
            password='testpass1234',
            first_name='firstname',
            last_name='Lastname'
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user_profile_success(self):
        """Test retrieve user."""
        res = self.client.get(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name
        })

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

        self.assertTrue(self.user.check_password(payload['password']))
        
    def test_retrieve_users_address_list(self):
        """Test list the users address"""
        ShippingAddress.objects.create(
            street='3000 swallow hill rd',
            building='112',
            city='pittsburgh',
            state='PA',
            zipcode=15220,
            customer=self.user
        )
        
        other_user = create_user(
            email='otheruser@example.com',
            password='otherpass1234'
        )
        ShippingAddress.objects.create(
            street='3000 swallow hill rd',
            building='112',
            city='pittsburgh',
            state='PA',
            zipcode=15220,
            customer=other_user
        )
        
        res = self.client.get(ADDRESS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(
            ShippingAddress.objects.filter(customer=self.user.id).count(), 1)

    def test_create_shipping_address(self):
        """Test create shipping address of user."""
        payload = {
            'street': '3000 swallow hill rd',
            'building': '112',
            'city': 'pittsburgh',
            'state': 'PA',
            'zipcode': 15220,
            'customer': self.user.id
        }

        res = self.client.post(ADDRESS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ShippingAddress.objects.filter(
            customer=self.user).count(), 1)

        serializer = AddressSerializer(data=payload)
        if serializer.is_valid():
            self.assertEqual(res.data, serializer.data)

    def test_create_address_invalid_data(self):
        invalid_data = {'user': self.user.id, 'city': 'Test City'}

        response = self.client.post(ADDRESS_URL, invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            ShippingAddress.objects.filter(customer=self.user).count(), 0)

    def test_patch_user_address(self):
        """Test update users address."""
        s_address = ShippingAddress.objects.create(
            street='Green tree rd',
            building=919,
            city='New jersey city',
            state='NJ',
            zipcode=12134,
            customer=self.user
        )
        
        payload = {
            'street': 'hope hollow',
            'building': 1010,
        }
        url = address_detail_url(s_address.id)
        res = self.client.patch(url, payload)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['street'], payload['street'])
        
    def test_delete_user_address(self):
        """Test delete users address."""
        s_address = ShippingAddress.objects.create(
            street='Green tree rd',
            building=919,
            city='New jersey city',
            state='NJ',
            zipcode=12134,
            customer=self.user
        )
        url = address_detail_url(s_address.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        
        
