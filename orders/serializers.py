from django.db import transaction
from rest_framework import serializers
from .models import OrderItem, Order
from carts.models import Basket
from django.utils.timezone import now

class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'discount', 'price_at_order', 'created', 'total_price']
        read_only_fields = ['price_at_order', 'created', 'total_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'basket', 'status', 'total_price', 'delivered_at', 'created', 'updated', 'items']
        read_only_fields = ['total_price', 'created', 'updated', 'items', 'basket', 'delivered_at']

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
                        discount=item.product.discount if hasattr(item.product, 'discount') else None,
                        price_at_order=item.product.price
                    )

                basket_items.delete()

                order.refresh_from_db()
                return order

        except Basket.DoesNotExist:
            raise serializers.ValidationError({"detail": "Basket not found"})

    def update(self, instance, validated_data):
        new_status = validated_data.get('status', instance.status)
        with transaction.atomic():
            if new_status == "cancelled" and instance.status != "cancelled":
                for item in instance.items.all():
                    product = item.product
                    product.stock += item.quantity
                    product.save()

            if new_status == "delivered" and instance.status != "delivered":
                instance.delivered_at = now()

            instance.status = new_status
            instance.save()
            instance.refresh_from_db()
            return instance