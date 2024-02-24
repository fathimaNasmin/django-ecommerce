"""
URL configuration for order app.
"""
from django.urls import path, include
from order import views

app_name = 'order'

urlpatterns = [
    path('payment/', views.PaymentView.as_view(), name='payment'),
    path('payment-return/', views.PaymentReturnView.as_view(),
         name='payment-return'),
    path('orders/', views.OrderView.as_view(), name='orders'),
]
