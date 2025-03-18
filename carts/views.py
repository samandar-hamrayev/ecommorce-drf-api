from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Basket, BasketItem
from .serializers import BasketItemSerializer, BasketSerializer


class BasketItemViewSet(ModelViewSet):
    serializer_class = BasketItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['product', 'quantity']
    search_fields = ['product__name', 'product__description']
    ordering_fields = ['quantity', 'added_at', 'product__price']
    ordering = ['-added_at']

    def get_queryset(self):
        user = self.request.user
        basket = Basket.objects.get(user=user)
        return BasketItem.objects.filter(basket=basket)

    def perform_create(self, serializer):
        serializer.save()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['basket'] = Basket.objects.get(user=self.request.user)
        return context


class BasketViewSet(ModelViewSet):
    serializer_class = BasketSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user', 'status']
    search_fields = ['user__email']
    ordering_fields = ['created', 'total_price']
    ordering = ['-created']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Basket.objects.all()
        return Basket.objects.filter(user=user)