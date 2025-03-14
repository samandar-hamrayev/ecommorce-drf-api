from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register(r'categories', views.CategoryListView, basename='category')
router.register('brands', views.BrandListView, basename='brand')
router.register('product-images', views.ProductImageView, basename='product-image')


urlpatterns = router.urls