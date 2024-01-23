"""Test admin site modification."""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


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
