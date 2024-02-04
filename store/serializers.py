"""Serializers for Store Models."""
from django.utils import timezone
from store.models import Category, SubCategory, Product, Inventory, Discount

from rest_framework import serializers


class SubCategorySerializer(serializers.ModelSerializer):
    """Serializer for subcategory."""
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all())

    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'category']


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category."""
    sub_category = SubCategorySerializer(many=True,
                                         read_only=False,
                                         required=False)

    class Meta:
        model = Category
        fields = ['id', 'name', 'sub_category']

    def create(self, validated_data):
        sub_category = validated_data.pop("sub_category", [])
        name = validated_data.get("name", None)

        if name:
            name = name.lower()
        try:
            category = Category.objects.get(name=name)
        except Category.DoesNotExist:
            category = Category.objects.create(name=name)

        if sub_category:
            for item in sub_category:
                SubCategory.objects.create(category=category, **item)
        return category


class InventorySerializer(serializers.ModelSerializer):
    """Serializer for inventory."""
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    modified_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Inventory
        fields = ['id', 'quantity', 'created_at', 'modified_at']


class DiscountSerializer(serializers.ModelSerializer):
    """Serializer for Discount."""
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    modified_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    valid_till = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Discount
        fields = ['id', 'percent', 'active',
                  'created_at', 'modified_at', 'valid_till']

    def validate_valid_till(self, date):
        """Validate valid_till date is a future date."""
        current_date = timezone.now().date()

        if date <= current_date:
            raise serializers.ValidationError(
                "The date should be a future date.")

        return date


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for products."""
    sub_category = SubCategorySerializer()
    product_inventory = InventorySerializer(read_only=True, many=True)
    discount = DiscountSerializer(read_only=True, many=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'image', 'description',
                  'product_inventory',
                  'discount',
                  'sub_category']
