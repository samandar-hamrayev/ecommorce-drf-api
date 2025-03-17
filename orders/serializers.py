from django.db import transaction
from rest_framework import serializers

from .models import OrderItem, Order

from carts.models import Basket


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'discount', 'price_at_order', 'created', 'delivered_at', 'total_price']
        read_only_fields = ['price_at_order', 'created', 'delivered_at', 'total_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'basket', 'status', 'total_price', 'created', 'updated', 'items']
        read_only_fields = ['total_price', 'created', 'updated', 'items']

    def create(self, validated_data):
        user = self.context['request'].user
        try:
            with transaction.atomic():
                basket = Basket.objects.get(user=user)
                basket_items = basket.items.all()

                if not basket_items:
                    raise serializers.ValidationError({"detail": "Basket is empty"})

                order = Order.objects.create(
                    basket=basket,
                    status='pending'
                )

                for item in basket_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        discount=item.product.discount if hasattr(item.product, 'discount') else None,  # Agar discount mahsulotda bo‘lsa
                        price_at_order=item.product.price
                    )

                basket_items.delete()

                order.refresh_from_db()
                return order

        except Basket.DoesNotExist:
            raise serializers.ValidationError({"detail": "Basket not found"})