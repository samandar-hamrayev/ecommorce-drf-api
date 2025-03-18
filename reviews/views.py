from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from products.permissions import IsOwner
from reviews.models import Review
from reviews.serializers import ReviewSerializer


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['product', 'user']
    search_fields = ['text']
    ordering_fields = ['created', 'value']
    ordering = ['-created']

    def get_permissions(self):

        if self.request.user.is_authenticated and self.request.user.is_superuser:
            return [IsAuthenticated()]


        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_superuser:
            queryset = Review.objects.select_related('user', 'product').prefetch_related(
                'product__order_items'
            )
        else:
            queryset = Review.objects.filter(user=self.request.user).select_related(
                'user', 'product'
            ).prefetch_related('product__order_items')

        product_pk = self.kwargs.get('product_pk')
        if product_pk:
            queryset = queryset.filter(product_id=product_pk)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['view'] = self
        return context