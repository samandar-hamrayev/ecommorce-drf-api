from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import (
    CategoryListSerializer, CategoryDetailSerializer, BrandListSerializer,
    BrandDetailSerializer, ProductListSerializer, ProductDetailSerializer,
    ProductImageSerializer, ProductFieldSerializer, ProductFieldValueSerializer
)

from .models import Category, Brand, Product, ProductImage, ProductField, ProductsFieldValue

from .filters import (
    ProductFilter, BrandFilter, CategoryFilter, ProductImageFilter,
    ProductFieldFilter, ProductFieldValueFilter
)

from .permissions import IsOwner
from rest_framework.serializers import ValidationError


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    filterset_class = CategoryFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created']
    ordering = ['name']

    def get_serializer_class(self):
        return CategoryListSerializer if self.action == 'list' else CategoryDetailSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAdminUser()]
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsOwner()]
        return [AllowAny()]


class BrandViewSet(ModelViewSet):
    queryset = Brand.objects.all()

    filterset_class = BrandFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created']
    ordering = ['name']

    def get_serializer_class(self):
        return BrandListSerializer if self.action == 'list' else BrandDetailSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAdminUser()]
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsOwner()]
        return [AllowAny()]


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()

    filterset_class = ProductFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_filters = ['price', 'stock', 'discount', 'created', 'average_rating']
    ordering = ['-created']

    def get_serializer_class(self):
        return ProductListSerializer if self.action == 'list' else ProductDetailSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAdminUser()]
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsOwner()]
        return [AllowAny()]

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.kwargs.get('category_pk')
        brand_id = self.kwargs.get('brand_pk')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if brand_id:
            queryset = queryset.filter(brand_id=brand_id)
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['view'] = self
        return context


class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer
    filterset_class = ProductImageFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['alt_text']
    ordering_fields = ['product', 'is_primary']
    ordering = ['-product']

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsOwner()]
        return [AllowAny()]

    def get_queryset(self):
        product_id = self.kwargs.get('product_pk')
        if not product_id:
            return ProductImage.objects.all()
        return ProductImage.objects.filter(product_id=product_id)

    def perform_create(self, serializer):
        product_id = self.kwargs.get('product_pk')
        product = Product.objects.get(id=product_id)
        if product.created_by != self.request.user:
            raise ValidationError({"error": "You are not the owner of this product."}, code=403)
        serializer.save()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        product_id = self.kwargs.get('product_pk')
        if product_id:
            context['product'] = Product.objects.get(id=product_id)
        return context


class ProductFieldViewSet(ModelViewSet):
    serializer_class = ProductFieldSerializer
    queryset = ProductField.objects.all()
    filterset_class = ProductFieldFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'field_type']
    ordering = ['name']

    def get_permissions(self):
        if self.action == 'create':
            return [IsAdminUser()]
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsOwner()]
        return [AllowAny()]


class ProductFieldValueViewSet(ModelViewSet):
    serializer_class = ProductFieldValueSerializer
    filterset_class = ProductFieldValueFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['value']
    ordering_fields = ['value', 'product']
    ordering = ['-product']

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsOwner()]
        return [AllowAny()]

    def get_queryset(self):
        product_id = self.kwargs.get('product_pk')
        if not product_id:
            raise ValidationError({"error": "Product ID is required."})
        return ProductsFieldValue.objects.filter(product_id=product_id)

    def perform_create(self, serializer):
        product_id = self.kwargs.get('product_pk')
        product = Product.objects.get(id=product_id)
        if product.created_by != self.request.user:
            raise ValidationError({"error": "You are not the owner of this product."}, code=403)
        serializer.save()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        product_id = self.kwargs.get('product_pk')
        if product_id:
            context['product'] = Product.objects.get(id=product_id)
        return context