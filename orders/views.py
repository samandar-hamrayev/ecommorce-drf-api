from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer


class OrderItemViewSet(ModelViewSet):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['product', 'quantity', 'order']
    search_fields = ['product__name', 'product__description']
    ordering_fields = ['quantity', 'created', 'price_at_order']
    ordering = ['-created']

    def get_queryset(self):
        return OrderItem.objects.filter(order__basket__user=self.request.user)


class OrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'basket', 'total_price']
    search_fields = ['basket__user__email']
    ordering_fields = ['created', 'total_price', 'delivered_at']
    ordering = ['-created']

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(basket__user=self.request.user)

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['POST'], url_path='make-order')
    def create_from_basket(self, request):
        serializer = OrderSerializer(data={}, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)