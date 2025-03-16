from django.urls import path, include
from rest_framework_nested.routers import DefaultRouter, NestedSimpleRouter
from .views import (
    CategoryViewSet, BrandViewSet, ProductViewSet,
    ProductImageViewSet, ProductFieldViewSet, ProductFieldValueViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'images', ProductImageViewSet, basename='images')
router.register(r'product-fields', ProductFieldViewSet, basename='product-field')


# nested url for category
category_router = NestedSimpleRouter(router, r'categories', lookup='category')
category_router.register(r'products', ProductViewSet, basename='category-products')

category_product_router = NestedSimpleRouter(category_router, r'products', lookup='product')
category_product_router.register(r'images', ProductImageViewSet, basename='category-product-images')
category_product_router.register(r'field-values', ProductFieldValueViewSet, basename='category-product-field-values')

# nested url for category
brand_router = NestedSimpleRouter(router, r'brands', lookup='brand')
brand_router.register(r'products', ProductViewSet, basename='brand-products')

brand_product_router = NestedSimpleRouter(brand_router, r'products', lookup='product')
brand_product_router.register(r'images', ProductImageViewSet, basename='brand-product-images')
brand_product_router.register(r'field-values', ProductFieldValueViewSet, basename='brand-product-field-values')

# nested url for products
product_router = NestedSimpleRouter(router, r'products', lookup='product')
product_router.register(r'images', ProductImageViewSet, basename='product-images')
product_router.register(r'field-values', ProductFieldValueViewSet, basename='product-field-values')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(category_router.urls)),
    path('', include(category_product_router.urls)),
    path('', include(brand_router.urls)),
    path('', include(brand_product_router.urls)),
    path('', include(product_router.urls)),
]