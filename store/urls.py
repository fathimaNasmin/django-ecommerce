"""
URL configuration for user app.
"""
from django.urls import path, include
from rest_framework import routers

from store import views  
# from store import views as store_views

router = routers.DefaultRouter()
router.register('category', views.CategoryViewSet)
router.register('sub-category', views.SubCategoryViewSet)
router.register('product', views.ProductViewSet)



urlpatterns = [
    path('', include(router.urls)),
]