from rest_framework import serializers, status

import users.serializers
from . import models



class ProductFieldValueSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField()
    field = serializers.SerializerMethodField()

    class Meta:
        model = models.ProductsFieldValue
        fields = ['field', 'value', 'product']
        read_only_fields = ['product', 'field']

    def get_product(self, obj):
        return ProductSerializer(obj.product, context=self.context).data

    def get_field(self, obj):
        return ProductFieldSerializer(obj.field, context=self.context).data



class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary']
        read_only_fields = ['created_by']


    def _update_primary_image(self, product, is_primary):
        """bitta productda is_primary imagening yagonaligin saqlash"""
        if is_primary:
            existing_images = models.ProductImage.objects.filter(product=product)
            existing_images.filter(is_primary=True).update(is_primary=False)

    def create(self, validated_data):
        product = validated_data.get('product')
        if not product and 'product' in self.context:
            product = self.context['product']
        if not product:
            raise serializers.ValidationError({"error": "Product is required."})

        is_primary = validated_data.get('is_primary', False)
        self._update_primary_image(product, is_primary)
        return super().create(validated_data)


    def update(self, instance, validated_data):
        product = validated_data.get('product', instance.product)
        is_primary = validated_data.get('is_primary', instance.is_primary)
        if product.created_by != self.context['request'].user:
            raise serializers.ValidationError(
                {"error": "You are not the creator of this project and cannot  update images"}
            )
        self._update_primary_image(product, is_primary)

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=models.Category.objects.all())
    brand = serializers.PrimaryKeyRelatedField(queryset=models.Brand.objects.all())
    created_by = serializers.SerializerMethodField()
    field_values = ProductFieldValueSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True)

    class Meta:
        model = models.Product
        fields = [
            'id', 'name', 'category', 'brand', 'created_by',
            'description', 'price', 'discounted_price', 'stock',
            'discount', 'created', 'updated', 'average_rating',
            'field_values', 'images'
        ]
        read_only_fields = [
            'discounted_price', 'average_rating',
            'created', 'updated'
        ]

    def get_created_by(self, obj):
        return users.serializers.UserSerializer(obj.created_by, context=self.context).data

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        validated_data['created_by'] = self.context['request'].user
        product = models.Product.objects.create(**validated_data)

        for image_data in images_data:
            image_serializer = ProductImageSerializer(
                data=image_data,
                context={**self.context, "product": product}
            )
            image_serializer.is_valid(raise_exception=True)
            image_serializer.save()
        return product

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images')
        instance = super().update(instance, validated_data)

        for image_data in images_data:
            image_serializer = ProductImageSerializer(
                data=image_data,
                context={**self.context, "product": instance}
            )
            image_serializer.is_valid(raise_exception=True)
            image_serializer.save()
        return instance


class CategorySerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    products = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = models.Category
        fields = ['id', 'name', 'description', 'created_by', 'created', 'updated', 'products']
        read_only_fields = ['created_by', 'product']

    def get_created_by(self, obj):
        user = self.context['request'].user

        if user.is_staff and user.is_superuser:
            return users.serializers.UserSerializer(obj.created_by).data

        return {
            "fullname": f"{obj.created_by.first_name} {obj.created_by.last_name}"
        }


    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class BrandSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    products = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    class Meta:
        model = models.Brand
        fields = ['id', 'name', 'description', 'logo', 'created_by', 'created','updated', 'products']
        read_only_fields = ['created_by', 'created','updated']

    def get_created_by(self, obj):
        user = self.context['request'].user

        if user.is_staff and user.is_superuser:
            return users.serializers.UserSerializer(obj.created_by).data

        return {
            "full name": f"{obj.created_by.first_name} {obj.created_by.last_name}"
        }
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ProductFieldSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ProductField
        fields = ['id', 'name', 'field_type', 'choices']









