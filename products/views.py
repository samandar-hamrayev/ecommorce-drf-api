from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, AllowAny

from . import  serializers
from . import models
from . import permissions

class CategoryListView(viewsets.ModelViewSet):
    serializer_class = serializers.CategorySerializer
    queryset = models.Category.objects.all()


    def get_permissions(self):
        if self.action == 'create':
            return [IsAdminUser()]

        if self.action in ('update', 'partial_update', 'destroy'):
            return [permissions.IsOwner()]

        return [AllowAny()]

class BrandListView(viewsets.ModelViewSet):
    serializer_class = serializers.BrandSerializer
    queryset = models.Brand.objects.all()

    def get_permissions(self):
        if self.action == 'create':
            return [IsAdminUser()]

        if self.action in ('update', 'partial_update', 'destroy'):
            return [permissions.IsOwner()]

        return [AllowAny()]

class ProductImageView(viewsets.ModelViewSet):
    serializer_class =  serializers.ProductImageSerializer
    queryset = models.ProductImage.objects.all()

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsProductOwner()]
        return [IsAdminUser()]

    def perform_create(self, serializer):
        product_id = self.request.data.get('product')
        product = models.Product.objects.get(id=product_id)
        return serializer.save()


    def get_queryset(self):
        if self.request.user.is_authenticated:
            return models.ProductImage.objects.filter(product__created_by=self.request.user)
        return models.ProductImage.objects.none()




