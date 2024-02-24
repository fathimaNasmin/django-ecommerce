"""Serializers for Order models."""
from rest_framework import serializers

from order.models import Order, OrderDetail, Payment
from store.models import Product

from store.serializers import ProductSerializer
from user.models import CartItem


class PaymentSerializer(serializers.ModelSerializer):
    """Serializers for payments."""
    class Meta:
        model = Payment
        fields = ['id', 'transaction_id', 'customer',
                  'order_amount', 'payment_method', 
                  'is_successful', 'timestamp']
        read_only_fields = ['id']
        
        
class OrderDetailSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderDetail
        fields = ['product', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderDetailSerializer(many=True,  source='orderdetail_set')

    class Meta:
        model = Order
        fields = ['order_id', 'amount',
                  'order_date', 'transaction_id', 'items']

    # def create(self, validated_data):
    #     order_items = validated_data.pop('items', [])
    #     order = Order.objects.create(**validated_data)
        
    #     for items in order_items:
    #         OrderDetail.objects.create(order=order,
    #                                    **items)
            
    #     # empty the cart of the user when the order is created.
    #     customer = validated_data['customer'] #add context={"user_id": self.request.user.id} in views when serializing
    #     try:
    #         cart_items = CartItem.objects.get(user=customer)
    #         cart_items.delete()
        
