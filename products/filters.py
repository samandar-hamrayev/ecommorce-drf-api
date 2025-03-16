from django_filters import rest_framework as filters
from .models import Product, Brand, Category, ProductImage, ProductField, ProductsFieldValue


class ProductFilter(filters.FilterSet):
    category = filters.NumberFilter(field_name='category__id', lookup_expr='exact')
    brand = filters.NumberFilter(field_name='brand__id', lookup_expr='exact')
    price_min = filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = filters.NumberFilter(field_name='price', lookup_expr='lte')
    stock_min = filters.NumberFilter(field_name='stock', lookup_expr='gte')
    stock_max = filters.NumberFilter(field_name='stock', lookup_expr='lte')
    discount = filters.BooleanFilter(field_name='discount', lookup_expr='gt', method='has_discount')


    def has_discount(self, quertset, name, value):
        if value:
            return quertset.filter(discount__gt=0)
        return quertset

    class Meta:
        model = Product
        fields = ['category', 'brand', 'price_min', 'price_max', 'stock_min', 'stock_max', 'discount']


class CategoryFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = Category
        fields = ['name', 'description']


class BrandFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = Brand
        fields = ['name', 'description']


class ProductImageFilter(filters.FilterSet):
    is_primary = filters.BooleanFilter()
    class Meta:
        model = ProductImage
        fields = ['is_primary']


class ProductFieldFilter(filters.FilterSet):
    field_type = filters.CharFilter(lookup_expr='exact')
    class Meta:
        model = ProductField
        fields = ['field_type']

class ProductFieldValueFilter(filters.FilterSet):
    field = filters.NumberFilter(field_name='field__id', lookup_expr='exact')
    value = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = ProductsFieldValue
        fields = ['field', 'value']

