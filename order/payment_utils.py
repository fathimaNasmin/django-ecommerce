import requests
import json
from django.conf import settings
from django.urls import reverse
# from decouple import config


def make_paypal_payment(amount):
    # Set up PayPal API credentials
    client_id = settings.PAYPAL_ID
    secret = settings.PAYPAL_SECRET
    url = settings.PAYPAL_BASE_URL
    
    # Set up API endpoints
    base_url = url
    token_url = base_url + '/v1/oauth2/token'
    payment_url = base_url + '/v1/payments/payment'

    # Request an access token
    token_payload = {'grant_type': 'client_credentials'}
    token_headers = {'Accept': 'application/json', 'Accept-Language': 'en_US'}
    token_response = requests.post(token_url, auth=(
        client_id, secret), data=token_payload, headers=token_headers)

    if token_response.status_code != 200:
        return False, "Failed to authenticate with PayPal API", None

    access_token = token_response.json()['access_token']

    # Create payment payload
    payment_payload = {
        'intent': 'sale',
        'payer': {
            'payment_method': 'paypal'
            },
        'transactions': [{
            'amount': {'total': str(amount), 'currency': 'USD'},
            'description': 'Purchase '
        }],
        'redirect_urls': {
            'return_url': reverse('order:payment-return'), # url after payment success
            'cancel_url': reverse('user:cart-list')
        }
    }

    # Create payment request
    payment_headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    payment_response = requests.post(payment_url, data=json.dumps(
        payment_payload), headers=payment_headers)
    # print(payment_response.text)
    
    if payment_response.status_code != 201:
        return False, None, None

    payment_id = payment_response.json()['id']
    approval_url = next(link['href'] for link in payment_response.json()[
                        'links'] if link['rel'] == 'approval_url')

    return True, payment_id, approval_url


def verify_paypal_payment(payment_id):
    # Set up PayPal API credentials
    client_id = settings.PAYPAL_ID
    secret = settings.PAYPAL_SECRET
    url = settings.PAYPAL_BASE_URL

    # Set up API endpoints
    base_url = url
    token_url = base_url + '/v1/oauth2/token'
    payment_url = base_url + '/v1/payments/payment'

    # Request an access token
    token_payload = {'grant_type': 'client_credentials'}
    token_headers = {'Accept': 'application/json', 'Accept-Language': 'en_US'}
    token_response = requests.post(token_url, auth=(
        client_id, secret), data=token_payload, headers=token_headers)

    if token_response.status_code != 200:
        raise Exception('Failed to authenticate with PayPal API.')

    access_token = token_response.json()['access_token']

    # Retrieve payment details
    payment_headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    payment_details_url = f'{payment_url}/{payment_id}'
    payment_details_response = requests.get(
        payment_details_url, headers=payment_headers)

    if payment_details_response.status_code != 200:
        raise Exception('Failed to retrieve PayPal payment details.')

    payment_status = payment_details_response.json()['state']
    
    if payment_status == 'created':
        return True
    else:
        # Payment failed or was canceled
        return False
