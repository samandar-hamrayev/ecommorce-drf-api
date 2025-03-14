from rest_framework import serializers, status

import users.serializers
from . import models

class CategorySerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    class Meta:
        model = models.Category
        fields = ['id', 'name', 'description', 'created_by', 'created', 'updated']
        read_only_fields = ['created_by']

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
    class Meta:
        model = models.Brand
        fields = ['id', 'name', 'description', 'logo', 'created_by', 'created','updated']
        read_only_fields = ['created_by', 'created','updated']

    def get_created_by(self, obj):
        user = self.context['request'].user

        if user.is_staff and user.is_superuser:
            return users.serializers.UserSerializer(obj.created_by).data

        return {
            "full name": f"{obj.created_by.first_name} {obj.created_by.last_name}"
        }
    def create(self, validated_data):
        validated_data['created_by'] = self.context['reqeust'].user
        return super().create(validated_data)


class ProductImageSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=models.Product.objects.all())

    class Meta:
        model = models.ProductImage
        fields = ['id', 'product', 'image', 'alt_text', 'is_primary']

    def create(self, validated_data):
        product = validated_data['product']
        if product.created_by != self.context['request'].user:
            raise serializers.ValidationError(
                {"error": "You are not the creator of this product and cannot add images."},
            code=403)
        return super().create(validated_data)
