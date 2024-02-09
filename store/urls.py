"""
URL configuration for user app.
"""
from django.urls import path, include
from rest_framework import routers

from store import views


router = routers.DefaultRouter()
router.register('category', views.CategoryViewSet)
router.register('sub-category', views.SubCategoryViewSet,
                basename='sub-category')
router.register('product', views.ProductViewSet)

app_name = 'store'


urlpatterns = [
    path('', include(router.urls)),
]
