"""Test for the order api endpoints."""
import json
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from django.contrib.auth import get_user_model

from order.tasks import send_order_confirmation_mail
from order.models import Order
from user.models import CartItem

from store.tests import test_store_api

from order.serializers import PaymentSerializer


PAYMENT_URL = reverse('order:payment')
PAYMENT_RETURN_VIEW = reverse('order:payment-return')
ORDER_URL = reverse('order:orders')


class PublicAPITests(TestCase):
    """Test the endpoints for unauthenticated users."""

    def test_retrieve_payment_url_unauthenticated_user(self):
        """Test retrieve payment url for unauthenticated user raises error."""
        res = self.client.get(PAYMENT_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_payment_url_unauthenticated_user(self):
        """Test the payment url for unauthenticated user raises error."""
        payload = {
            'total_amount': 12.99
        }
        res = self.client.post(PAYMENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_payment_return_url_unauthenticated_user(self):
        """Test retrieve payment return url for unauthenticated user raises error."""
        res = self.client.get(PAYMENT_RETURN_VIEW)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_payment_return_url_unauthenticated_user(self):
        """Test the payment url for unauthenticated user raises error."""
        payload = {
            'total_amount': 12.99
        }
        res = self.client.post(PAYMENT_RETURN_VIEW, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PrivateAPITests(TestCase):
    """Test the endpoints for authenticated users."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            password='testpass1234'
        )
        self.client.force_authenticate(self.user)

    # @patch('order.views.payment_utils.make_paypal_payment')
    # @patch('order.views.PaymentSerializer.create')
    # def test_successful_payment_for_the_order(self, mock_make_paypal_payment, mock_payment_serializer):
    #     """Test the payment page url to make an order."""

    #     # Mock return value of paypal payment
    #     mock_make_paypal_payment.return_value = (
    #         True, 'fake_payment_id', 'fake_approval_url')
    #     payload = {
    #         'total_amount': 12.99
    #     }
    #     res = self.client.post(PAYMENT_URL, payload)
    #     print("Mocked make_paypal_payment response:", mock_make_paypal_payment.return_value)
    #     print("Actual response:", res.content)

    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertIn('payment_id', res.data)
    #     self.assertIn('approval_url', res.data)

    #     expected_data = {
    #         'transaction_id': 'fake_payment_id',
    #         'customer': self.user.id,
    #         'order_amount': payload['total_amount'],
    #         'payment_method': 'paypal'
    #     }

    #     mock_make_paypal_payment.assert_called_once_with('12.99')

    #     mock_payment_serializer.create.assert_called_once_with(expected_data)
    # def test_payment_url_for_the_order(self):
    #     """Test the payment page url to make an order."""
    #     payload = {
    #         'total_amount': 12.99
    #     }
    #     res = self.client.post(PAYMENT_URL, payload)

    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     response_data = json.loads(res.content.decode('utf-8'))
    #     self.assertIn('payment_id', response_data)
    #     self.assertIn('approval url', response_data)

    # def test_retrieve_payment_url_error(self):
    #     """Test retrieve the payment url raises error."""
    #     res = self.client.get(PAYMENT_URL)

    #     self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # def test_retrieve_payment_return_url_error(self):
    #     """Test retrieve the payment url raises error."""
    #     res = self.client.get(PAYMENT_RETURN_VIEW)

    #     self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # def test_payment_return_url(self):
    #     """Test the payment return that checks the status and create an order."""
    #     # add product

    #     product_no1 = test_store_api.create_product(
    #         name='spoon', price=2.99, description="Set of 6 stainless steel spoons")
    #     product_no2 = test_store_api.create_product(
    #         name='bedsheet', price=52.98, description="A queen size cotton bedsheet")
    #     # add product to cart
    #     CartItem.objects.create(
    #         product=product_no1,
    #         quantity=2,
    #         user=self.user
    #     )
    #     CartItem.objects.create(
    #         product=product_no2,
    #         quantity=1,
    #         user=self.user
    #     )
    #     cart_items = CartItem.objects.filter(user=self.user)
    #     total_amount = sum([item.total_cart_amount() for item in cart_items])

    #     payload = {
    #         'total_amount': total_amount
    #     }
    #     res = self.client.post(PAYMENT_URL, payload)

    #     payment_id = res.data['payment_id']

    #     res = self.client.post(PAYMENT_RETURN_VIEW, {'payment_id': payment_id})
    #     print(res.content)
    #     self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    # def test_retrieve_customer_orders(self):
    #     """Test the retrieval of customer order."""
    #     res = self.client.get(ORDER_URL)

    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertIn('count', res.data)
    #     self.assertIn('next', res.data)
    #     self.assertIn('previous', res.data)
    #     self.assertIn('results', res.data)

    # def test_order_confirmation_mail(self):
    #     """Test the order confirmation mail sent to the customer."""
    #     order = Order.objects.create(
    #         customer=self.user,
    #         amount=10.99
    #     )
    #     print(order)
