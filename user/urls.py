"""
URL configuration for user app.
"""
from django.urls import path, include
from user import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('address', views.UserAddressView, basename='address')
router.register('cart', views.CartItemUserView, basename='cart')

app_name = 'user'

urlpatterns = [
    path('register/', views.CreateUserView.as_view(), name='register'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('profile/', views.ManageUserProfileView.as_view(), name='profile'),
    path('', include(router.urls)),

]

