from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response

from . import  serializers
from . import models
from . import permissions

class CategoryListViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CategorySerializer
    queryset = models.Category.objects.all()


    def get_permissions(self):
        if self.action == 'create':
            return [IsAdminUser()]

        if self.action in ('update', 'partial_update', 'destroy'):
            return [permissions.IsOwner()]

        return [AllowAny()]

class BrandListViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.BrandSerializer
    queryset = models.Brand.objects.all()

    def get_permissions(self):
        if self.action == 'create':
            return [IsAdminUser()]

        if self.action in ('update', 'partial_update', 'destroy'):
            return [permissions.IsOwner()]

        return [AllowAny()]

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ProductSerializer
    queryset = models.Product.objects.all()

    def get_permissions(self):
        if self.action == 'create':
            return [IsAdminUser()]

        if self.action in ('update', 'partial_update', 'destroy'):
            return [permissions.IsOwner()]

        return [AllowAny()]



class ProductFieldViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ProductFieldSerializer
    queryset = models.ProductField.objects.all()

    def get_permissions(self):
        if self.action in ('create', 'updade', 'destroy', 'partial_update'):
            return [IsAdminUser()]
        return [AllowAny()]

class ProductFieldValueViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ProductFieldValueSerializer
    queryset = models.ProductsFieldValue.objects.all()

    def get_permissions(self):
        return [IsAdminUser()]






