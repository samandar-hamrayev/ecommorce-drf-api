from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import ModelViewSet
from .models import Basket, BasketItem
from .serializers import BasketItemSerializer, BasketSerializer

class BasketItemViewSet(ModelViewSet):
    serializer_class = BasketItemSerializer
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAdminUser]
    http_method_names = ['get']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Basket.objects.all()
        return Basket.objects.filter(user=user)