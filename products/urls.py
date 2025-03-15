from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register(r'categories', views.CategoryListViewSet, basename='category')
router.register(r'brands', views.BrandListViewSet, basename='brand')
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'product-fields', views.ProductFieldViewSet, basename='product-field')
router.register(r'product-field-values', views.ProductFieldValueViewSet, basename='product-field-value')


urlpatterns = router.urls