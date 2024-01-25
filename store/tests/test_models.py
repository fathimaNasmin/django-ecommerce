"""Tests the Store models
"""

from django.test import TestCase
from store import models

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError


class StoreModelTests(TestCase):
    """Test cases for store model."""
    def setUp(self):
        self.category1 = models.Category.objects.create(
            name='cat1'
        )
        self.category2 = models.Category.objects.create(
            name='cat2'
        )
    
    def test_category_success(self):
        """test the creation of category success."""
        category_obj = models.Category.objects.all()
        self.assertEqual(category_obj.count(), 2)
        
    def test_category_unique_name(self):
        """Test the unique name of the category."""
        with self.assertRaises(IntegrityError):
            models.Category.objects.create(name='cat1')
            
    def test_category_empty_name_error(self):
        """Test the empty category name raises error."""
        empty_category = models.Category.objects.create(name='')
        self.assertRaises(ValidationError, empty_category.full_clean)
        
    def test_subcategory_success(self):
        """test the creation of category success."""
        subcategory1 = models.SubCategory.objects.create(
            name='subcat1',
            category=self.category1
        )
        subcategory_obj = models.SubCategory.objects.all()
        self.assertEqual(subcategory_obj.count(), 1)
        
    def test_subcategory_unique_name(self):
        """Test the unique name of the category."""
        models.SubCategory.objects.create(
            name='cat1',
            category=self.category1
        )
        
        with self.assertRaises(IntegrityError):
            models.SubCategory.objects.create(
                name='cat1', 
                category=self.category1)
    
    def test_subcategory_empty_name_error(self):
        """Test the empty category name raises error."""
        empty_category = models.SubCategory.objects.create(
            name='', category=self.category1)
        
        self.assertRaises(ValidationError, empty_category.full_clean)
        
    def test_subcategory_unique_name_different_category(self):
        """Test subcategory name uniqueness with different category."""
        models.SubCategory.objects.create(
            name='subcat1',
            category=self.category1
        )
        models.SubCategory.objects.create(
            name='subcat1',
            category=self.category2
        )
        
        self.assertEqual(models.SubCategory.objects.count(), 2)