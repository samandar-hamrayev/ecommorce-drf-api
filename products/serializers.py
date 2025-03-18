from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField, SerializerMethodField, ValidationError
from .models import Category, Brand, Product, ProductImage, ProductField, ProductsFieldValue
from users.serializers import UserSerializer


class ProductFieldSerializer(ModelSerializer):
    class Meta:
        model = ProductField
        fields = ['id', 'name', 'field_type', 'choices']


class ProductImageSerializer(ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary']
        read_only_fields = ['id']

    def _update_primary_image(self, product, is_primary):
        if is_primary:
            ProductImage.objects.filter(product=product, is_primary=True).update(is_primary=False)

    def create(self, validated_data):
        product = self.context.get('product')
        if not product:
            raise ValidationError({"error": "Product is required."})
        if product.created_by != self.context['request'].user:
            raise ValidationError({"error": "You are not the owner of this product."}, code=403)
        is_primary = validated_data.get('is_primary', False)
        self._update_primary_image(product, is_primary)
        validated_data['product'] = product
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if instance.product.created_by != self.context['request'].user:
            raise ValidationError({"error": "You are not the owner of this product."}, code=403)
        is_primary = validated_data.get('is_primary', instance.is_primary)
        self._update_primary_image(instance.product, is_primary)
        return super().update(instance, validated_data)


class ProductFieldValueSerializer(ModelSerializer):
    field = PrimaryKeyRelatedField(queryset=ProductField.objects.all())

    class Meta:
        model = ProductsFieldValue
        fields = ['id', 'field', 'value']

    def create(self, validated_data):
        product = self.context.get('product')
        if not product:
            raise ValidationError({"error": "Product is required."})
        if product.created_by != self.context['request'].user:
            raise ValidationError({"error": "You are not the owner of this product."}, code=403)
        validated_data['product'] = product
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if instance.product.created_by != self.context['request'].user:
            raise ValidationError({"error": "You are not the owner of this product."}, code=403)
        return super().update(instance, validated_data)


class CategoryListSerializer(ModelSerializer):
    products = PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description','products']


class CategoryDetailSerializer(ModelSerializer):
    created_by = SerializerMethodField()
    products = SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_by', 'created', 'updated', 'products']
        read_only_fields = ['created_by', 'created', 'updated']

    def get_created_by(self, obj):
        user = self.context['request'].user
        if user.is_staff and user.is_superuser:
            return UserSerializer(obj.created_by).data
        return {"fullname": f"{obj.created_by.first_name} {obj.created_by.last_name}"}

    def get_products(self, obj):
        products = obj.products.all()
        return ProductListSerializer(products, many=True, context=self.context).data

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class BrandListSerializer(ModelSerializer):
    products = PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Brand
        fields = ['id', 'name', 'description', 'logo', 'products']


class BrandDetailSerializer(ModelSerializer):
    created_by = SerializerMethodField()
    products = SerializerMethodField()

    class Meta:
        model = Brand
        fields = ['id', 'name', 'description', 'logo', 'created_by', 'created', 'updated', 'products']
        read_only_fields = ['created_by', 'created', 'updated']

    def get_created_by(self, obj):
        user = self.context['request'].user
        if user.is_staff and user.is_superuser:
            return UserSerializer(obj.created_by).data
        return {"full_name": f"{obj.created_by.first_name} {obj.created_by.last_name}"}

    def get_products(self, obj):
        products = obj.products.all()
        return ProductListSerializer(products, many=True, context=self.context).data

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ProductListSerializer(ModelSerializer):
    category = CategoryListSerializer(read_only=True)
    brand = BrandListSerializer(read_only=True)
    created_by = SerializerMethodField()
    primary_image = SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'brand', 'created_by', 'description', 'price',
                  'discounted_price', 'stock', 'discount', 'created', 'updated', 'average_rating',
                  'primary_image']
        read_only_fields = ['discounted_price', 'average_rating', 'created', 'updated']

    def get_created_by(self, obj):
        return UserSerializer(obj.created_by, context=self.context).data

    def get_primary_image(self, obj):
        primary = obj.images.filter(is_primary=True).first()
        return ProductImageSerializer(primary, context=self.context).data if primary else None


class ProductDetailSerializer(ModelSerializer):
    category = PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False)
    brand = PrimaryKeyRelatedField(queryset=Brand.objects.all(), required=False)
    created_by = SerializerMethodField()
    field_values = ProductFieldValueSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'brand', 'created_by', 'description', 'price',
                  'discounted_price', 'stock', 'discount', 'created', 'updated', 'average_rating',
                  'field_values', 'images']
        read_only_fields = ['discounted_price', 'average_rating', 'created', 'updated', 'created_by']

    def get_created_by(self, obj):
        return UserSerializer(obj.created_by, context=self.context).data

    def validate(self, attrs):
        category = attrs.get('category')
        brand = attrs.get('brand')
        view = self.context.get('view')

        if not category and view:
            category_id = view.kwargs.get('category_pk')
            if category_id:
                try:
                    attrs['category'] = Category.objects.get(id=category_id)
                except Category.DoesNotExist:
                    raise ValidationError({"category": "Category from URL does not exist."})
        if not brand and view:
            brand_id = view.kwargs.get('brand_pk')
            if brand_id:
                try:
                    attrs['brand'] = Brand.objects.get(id=brand_id)
                except Brand.DoesNotExist:
                    raise ValidationError({"brand": "Brand from URL does not exist."})


        if not attrs.get('category'):
            raise ValidationError({"category": "This field is required."})
        if not attrs.get('brand'):
            raise ValidationError({"brand": "This field is required."})

        return attrs

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        validated_data['created_by'] = self.context['request'].user
        product = Product.objects.create(**validated_data)

        for image_data in images_data:
            image_serializer = ProductImageSerializer(
                data=image_data,
                context={**self.context, 'product': product}
            )
            image_serializer.is_valid(raise_exception=True)
            image_serializer.save()
        return product

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', None)
        instance = super().update(instance, validated_data)

        if images_data is not None:
            for image_data in images_data:
                image_serializer = ProductImageSerializer(
                    data=image_data,
                    context={**self.context, 'product': instance}
                )
                image_serializer.is_valid(raise_exception=True)
                image_serializer.save()
        return instance