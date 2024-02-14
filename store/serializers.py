"""Serializers for Store Models."""
from django.db import IntegrityError
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
        read_only_fields = ['id']


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category."""
    sub_category = SubCategorySerializer(many=True,
                                         read_only=False,
                                         required=False)

    class Meta:
        model = Category
        fields = ['id', 'name', 'sub_category']
        read_only_fields = ['id']

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
    created_at = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False)
    modified_at = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False)

    class Meta:
        model = Inventory
        fields = ['id', 'quantity', 'created_at', 'modified_at']
        read_only_fields = ['id']


class DiscountSerializer(serializers.ModelSerializer):
    """Serializer for Discount."""
    created_at = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False)
    modified_at = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False)
    valid_till = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False)

    class Meta:
        model = Discount
        fields = ['id', 'percent', 'active',
                  'created_at', 'modified_at', 'valid_till']
        read_only_fields = ['id']

    def validate_valid_till(self, date):
        """Validate valid_till date is a future date."""
        current_date = timezone.now()

        if date <= current_date:
            raise serializers.ValidationError(
                "The date should be a future date.")

        return date


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for products."""
    sub_category = serializers.PrimaryKeyRelatedField(
        queryset=SubCategory.objects.all())
    product_inventory = InventorySerializer(many=True, required=False)
    discount = DiscountSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'image', 'description',
                  'product_inventory',
                  'discount',
                  'sub_category']
        read_only_fields = ['id']

    def _get_or_create_inventory(self, inventory, product):
        """Helper fuction to get or create an inventory."""
        inv, created = Inventory.objects.get_or_create(product=product)
        for item in inventory:
            inv.quantity = item['quantity']
        return inv

    def validate_name(self, name):
        """Validate name of the product if it already exists."""
        name_exists = Product.objects.filter(name=name).exists()

        if name_exists:
            raise serializers.ValidationError("This product already exists.")

        return name

    def create(self, validated_data):
        product_inventory_data = validated_data.pop('product_inventory', [])
        discount_data = validated_data.pop('discount', [])

        # Create Product instance
        product = Product.objects.create(**validated_data)

        # Create inventory instance
        try:
            if product_inventory_data:
                new_inventory = self._get_or_create_inventory(
                    product_inventory_data,
                    product)
                product.product_inventory.add(new_inventory)
        except Exception as e:
            print("Inv not created: ", e)

        # Create discount instance
        try:
            if discount_data:
                for discounted_item in discount_data:
                    discount_instance = Discount.objects.create(product=product,
                                                                **discounted_item)
                    product.discount.add(discount_instance)
        except Exception as e:
            print("Discount is empty: ", e)

        return product

    def update(self, instance, validated_data):
        product_inventory_data = validated_data.pop('product_inventory', None)
        discount_data = validated_data.pop('discount', [])

        if product_inventory_data is not None:
            inv = self._get_or_create_inventory(product_inventory_data,
                                                instance)
            instance.product_inventory.update(quantity=inv.quantity)

        if discount_data:
            for item in discount_data:
                discount, created = Discount.objects.update_or_create(
                    defaults=item,
                    product=instance
                )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images."""

    class Meta:
        model = Product
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': 'True'}}
