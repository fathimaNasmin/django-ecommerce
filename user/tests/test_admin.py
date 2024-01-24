"""Test admin site modification."""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from user.models import ShippingAddress


class AdminSiteTests(TestCase):
    """Test for Django admin."""
    
    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='testpass224'
        )
        self.client.force_login(self.admin_user)
        
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='test12345'
        )
        self.address = ShippingAddress.objects.create(
            street='abc street',
            building='123',
            city='jersey',
            state='NJ',
            zipcode=15222,
            customer=self.user
        )
        
    def test_user_lists(self):
        """Test the users are listed on the page."""
        url = reverse('admin:user_user_changelist')
        res = self.client.get(url)
        
        self.assertContains(res, self.user.email)
        self.assertContains(res, self.user.first_name)
        
    def test_user_edit_page(self):
        """Test the edit user page works."""
        url = reverse('admin:user_user_change', args=[self.user.id])
        res = self.client.get(url)
        
        self.assertEqual(res.status_code, 200)
        
    def test_create_user_page(self):
        """Test create user page works."""
        url = reverse('admin:user_user_add')
        res = self.client.get(url)
        
        self.assertEqual(res.status_code, 200)
        
    def test_shipping_address_lists(self):
        """Test the users shipping address are listed on the page."""
        url = reverse('admin:user_shippingaddress_changelist')
        res = self.client.get(url)
        
        self.assertContains(res, self.address.street)
        
    def test_shipping_address_edit_page(self):
        """Test the edit shipping address page works."""
        url = reverse('admin:user_shippingaddress_change', 
                      args=[self.address.id])
        res = self.client.get(url)
        
        self.assertEqual(res.status_code, 200)
        
    def test_create_address_page(self):
        """Test create user address page works."""
        url = reverse('admin:user_shippingaddress_add')
        res = self.client.get(url)
        
        self.assertEqual(res.status_code, 200)
        
    def test_listing_users_address_inline(self):
        """Test listing the users address in the users edit page."""
        url = reverse('admin:user_user_change', args=[self.user.id])
        res = self.client.get(url)
        
        self.assertContains(res, 'Shipping Address')
        
        self.assertContains(res, 'abc street')
        self.assertContains(res, 123)
        self.assertContains(res, 'jersey')
        self.assertContains(res, 'NJ')
        self.assertContains(res, '15222')
        
    def test_listing_users_address_readonly_inline(self):
        """Test listing the users address in the users edit page."""
        url = reverse('admin:user_user_change', args=[self.user.id])
        res = self.client.get(url)
        
        self.assertContains(res, 'readonly')
        
    def test_listing_multiple_users_address_inline(self):
        """Test listing multiple address
        of users inline in users page."""
        new_address = ShippingAddress.objects.create(
            street='test street',
            building='111',
            city='city',
            state='state',
            zipcode=10101,
            customer=self.user
        )
        url = reverse('admin:user_user_change', args=[self.user.id])
        res = self.client.get(url)
        
        self.assertContains(res, 'test street')
        self.assertContains(res, '111')
        self.assertContains(res, 'city')
        self.assertContains(res, 'state')
        self.assertContains(res, 10101)
        
