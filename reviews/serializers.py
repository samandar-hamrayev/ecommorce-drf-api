from rest_framework import serializers

from orders.models import OrderItem
from products.models import Product
from reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.email', read_only=True)


    class Meta:
        model = Review
        fields = ['id', 'user', 'product', 'text', 'value', 'created', 'updated']
        read_only_fields = ['id', 'user', 'created', 'updated']

    def validate(self, attrs):
        request = self.context['request']
        product = attrs.get('product')
        view = attrs.get('view')

        if not product and view:
            product_id = view.kwargs.get('product_pk')
            if product_id:
                try:
                    attrs['product'] = Product.objects.get(id=product_id)
                except Product.DoesNotExist:
                    raise serializers.ValidationError({"product": "Product does not exist."})
            else:
                raise serializers.ValidationError({"product": "Product is required."})

        if not product:
            raise serializers.ValidationError({"product": "Product is required."})

        user = request.user
        has_purchased = OrderItem.objects.filter(
            order__basket__user = user,
            product=product,
            order__status = 'delivered'
        ).exists()
        if not has_purchased:
            raise serializers.ValidationError({"error": "You can only review products you have purchased and received."})

        if not attrs.get('text') and not attrs.get('value'):
            raise serializers.ValidationError({"error": "At least one of 'text' or 'value' must be provided."})

        return attrs

    def create(self, validated_data):
        user = validated_data['user']
        product = validated_data['product']

        has_already = Review.objects.filter(user=user, product=product).exists()
        if has_already:
            raise serializers.ValidationError({"detail": "You can only review one product once."})
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if instance.user != self.context['request'].user:
            raise serializers.ValidationError({"error": "You can only edit your own reviews."})
        return super().update(instance, validated_data)




