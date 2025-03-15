from django.contrib import admin
from . import models

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    model = models.Product
    list_display = [field.name for field in models.Product._meta.fields]


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in models.Category._meta.fields]

@admin.register(models.Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = [field.name for field in models.Brand._meta.fields]

@admin.register(models.ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = [field.name for field in models.ProductImage._meta.fields]


@admin.register(models.ProductField)
class ProductFieldAdmin(admin.ModelAdmin):
    list_display = [field.name for field in models.ProductField._meta.fields]


@admin.register(models.ProductsFieldValue)
class ProductsFieldValueAdmin(admin.ModelAdmin):
    list_display = [field.name for field in models.ProductsFieldValue._meta.fields]