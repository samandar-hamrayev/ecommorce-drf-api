from rest_framework import serializers
from .models import Basket, BasketItem
from products.serializers import ProductListSerializer
from users.serializers import UserSerializer
from products.models import Product
from rest_framework.response import Response


class BasketItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = BasketItem
        fields = ['id', 'product', 'product_id', 'quantity', 'added_at', 'total_price']
        read_only_fields = ['added_at']

    def create(self, validated_data):
        basket = self.context['basket']
        product = validated_data['product']
        quantity = validated_data['quantity']


        if quantity < 1:
            raise serializers.ValidationError({"error": "You must purchase at least 1 product"})

        if quantity <= product.stock:
            product.stock -= quantity
            product.save()
        else:
            raise serializers.ValidationError({
                "quantity": f"Only {product.stock} items available in stock."
            })

        existing_item = BasketItem.objects.filter(basket=basket, product=product).first()
        if existing_item:
            existing_item.quantity += quantity
            existing_item.save()
            return existing_item

        return BasketItem.objects.create(basket=basket, **validated_data)

    def update(self, instance, validated_data):
        basket = self.context['basket']
        quantity = validated_data.get('quantity', instance.quantity)

        quantity_diff = quantity - instance.quantity

        if quantity_diff > 0:
            if quantity_diff <= instance.product.stock:
                instance.product.stock -= quantity_diff
                instance.product.save()
            else:
                raise serializers.ValidationError({
                    "quantity": f"Only {instance.product.stock} items available in stock."
                })
        elif quantity_diff < 0:
            instance.product.stock -= quantity_diff
            instance.product.save()

        instance.quantity = quantity
        if instance.quantity <= 0:
            instance.product.stock += instance.quantity
            instance.product.save()
            instance.delete()
            return Response({"message": f"The {instance.product.name} in your basket has been removed."})
        else:
            instance.save()
        return instance


class BasketSerializer(serializers.ModelSerializer):
    items = BasketItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Basket
        fields = ['id', 'user', 'items', 'created', 'updated', 'total_price']
        read_only_fields = ['user', 'created', 'updated']