"""Tests for user api endpoint."""

from decimal import Decimal
from django.test import TestCase
from django.urls import reverse

from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from user.serializers import AddressSerializer
from user.models import ShippingAddress, CartItem

from store.models import Product

from store.tests import test_store_api

CREATE_USER_URL = reverse('user:register')
TOKEN_URL = reverse('user:token')
PROFILE_URL = reverse('user:profile')
ADDRESS_URL = reverse('user:address-list')
CART_URL = reverse('user:cart')


def address_detail_url(address_id):
    """Create and return detail url for address."""
    return reverse('user:address-detail', args=[address_id])


def cart_detail_url(item_id):
    """Create and return cart detail url."""
    return reverse('user:cart-detail', args=[item_id])


def create_user(**params):
    """Create and returns new user."""
    return get_user_model().objects.create_user(**params)


# Helper function for creating new product instance.
def create_product(name='sample product',
                   price='20.99',
                   description='sample product description'):
    """Create and returns product."""
    category = test_store_api.create_category()
    sub_category = test_store_api.create_sub_category(category=category)

    return Product.objects.create(
        name=name,
        price=Decimal(price),
        description=description,
        sub_category=sub_category
    )


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
        
    def test_retrieve_cart_unauthorized_user(self):
        """Test retrieve cart by unauthorized user."""
        res = self.client.get(CART_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_post_cart_unauthorized_user(self):
        """Test post cart by unauthorized user."""
        res = self.client.post(CART_URL, {})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


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
        
    def test_retrieve_cart_user(self):
        """Test retrieve cart of user."""
        product1 = test_store_api.create_product(name='product1')
        CartItem.objects.create(
            user=self.user,
            product=product1,
            quantity=2
        )
        res = self.client.get(CART_URL)
        
        cart_item = CartItem.objects.filter(user=self.user)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(cart_item.count(), 1)
        
    def test_post_item_cart_user(self):
        """Test creating new item to the cart of the user."""
        product1 = test_store_api.create_product(name='product1')
        product2 = test_store_api.create_product(name='product2')

        CartItem.objects.create(
            user=self.user,
            product=product1,
            quantity=2
        )
        
        payload = {
            'user': self.user,
            'product': product2,
            'quantity': 1
        }
        
        res = self.client.post(CART_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        
        cart_items = CartItem.objects.filter(user=self.user)
        for items in cart_items:
            self.assertEqual(items.product, res.data['product'])
            self.assertEqual(items.quantity, res.data['quantity'])
            
    def test_patch_cart_item(self):
        """Test updating the cart item."""
        product1 = test_store_api.create_product(name='product1')
        item1 = CartItem.objects.create(
            user=self.user,
            product=product1,
            quantity=2
        )
        
        payload = {
            'user': self.user,
            'product': product1,
            'quantity': 1
        }
        url = cart_detail_url(item1.id)
        res = self.client.patch(url, payload)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            CartItem.objects.filter(user=self.user)[0].quantity, 1
        )

    def test_delete_item_from_user_cart(self):
        """Test delete item from thr users cart."""
        product1 = test_store_api.create_product(name='product1')
        product2 = test_store_api.create_product(name='product2')
        item1 = CartItem.objects.create(
            user=self.user,
            product=product1,
            quantity=2
        )
        item2 = CartItem.objects.create(
            user=self.user,
            product=product2,
            quantity=5
        )
        url = cart_detail_url(item1.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        no_item_exists = CartItem.objects.filter(user=self.user, product=product1).exists()
        self.assertFalse(no_item_exists)
        item_exists = CartItem.objects.filter(
            user=self.user, product=product2).exists()
        self.assertTrue(item_exists)

        
        
