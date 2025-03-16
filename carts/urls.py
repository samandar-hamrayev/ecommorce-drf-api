from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BasketViewSet, BasketItemViewSet


router = DefaultRouter()
router.register(r'baskets', BasketViewSet, basename='basket')
router.register(r'my-basket', BasketItemViewSet, basename='my-basket')

urlpatterns = [
    path('', include(router.urls)),
]