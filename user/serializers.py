"""Serializers for user api view."""

from django.contrib.auth import (
    get_user_model,
    authenticate
)
from django.utils.translation import gettext as _
from user.models import ShippingAddress, CartItem
from store.models import Product

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer class for user model."""

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}

    def create(self, validated_data):
        """Create and returns encrypted password."""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return user."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for user auth token."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate user."""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if not user:
            msg = _('Unable to authenticate with provided credentials.')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for Shipping Address of customer."""
    zipcode = serializers.IntegerField()
    customer = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all())

    class Meta:
        model = ShippingAddress
        fields = ['street', 'building', 'city',
                  'state', 'zipcode', 'customer']

    def validate_zipcode(self, code):
        """Validate zipcode."""
        if code > 0 and len(str(abs(code))) == 5:
            return code
        else:
            raise serializers.ValidationError(
                "Invalid zipcode.Enter an valid zipcode")


class CartSerializer(serializers.ModelSerializer):
    """Serializer for cart items of customer/user."""
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = CartItem
        fields = ['product', 'quantity']

    def validate_quantity(self, quantity):
        """Validate number of quantity."""
        if quantity < 1:
            raise serializers.ValidationError("Minimum quantity is 1.")
        return quantity
