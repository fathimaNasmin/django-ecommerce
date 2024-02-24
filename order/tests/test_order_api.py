"""Test for the order api endpoints."""
import json
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from django.contrib.auth import get_user_model

PAYMENT_URL = reverse('order:payment')
PAYMENT_RETURN_VIEW = reverse('order:payment-return')


class PrivateAPITests(TestCase):
    """Test the endpoints for authenticated users."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            password='testpass1234'
        )
        self.client.force_authenticate(self.user)

    def test_payment_url_for_the_order(self):
        """Test the payment page url to make an order."""
        payload = {
            'total_amount': 12.99
        }
        res = self.client.post(PAYMENT_URL, payload)
        # print(res.content)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        response_data = json.loads(res.content.decode('utf-8'))
        self.assertIn('payment_id', response_data)
        self.assertIn('approval url', response_data)

    def test_payment_return_url(self):
        """Test the payment return that checks the status and create an order."""
        # add product
        from store.tests import test_store_api
        from user.models import CartItem
        product_no1 = test_store_api.create_product(name='spoon', price=2.99, description="Set of 6 stainless steel spoons")
        product_no2 = test_store_api.create_product(
            name='bedsheet', price=52.98, description="A queen size cotton bedsheet")
        # add product to cart 
        CartItem.objects.create(
            product=product_no1,
            quantity=2,
            user=self.user
        )
        CartItem.objects.create(
            product=product_no2,
            quantity=1,
            user=self.user
        )
        cart_items = CartItem.objects.filter(user=self.user)
        total_amount = sum([item.total_cart_amount() for item in cart_items])
        print('total_amount:', total_amount)
        
        payload = {
            'total_amount': total_amount
        }
        res = self.client.post(PAYMENT_URL, payload)

        payment_id = res.data['payment_id']
        
        res = self.client.post(PAYMENT_RETURN_VIEW, {'payment_id': payment_id})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
