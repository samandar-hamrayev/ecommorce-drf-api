from django.contrib import admin
from . import models

class CategoryAdmin(admin.ModelAdmin):
    model = models.Category
    list_display = ['id', 'name']

class ProductAdmin(admin.ModelAdmin):
    model = models.Product
    list_display = ['id', 'name']



admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Brand, ProductAdmin)
admin.site.register(models.ProductImage)
admin.site.register(models.Product)
admin.site.register(models.ProductField)
admin.site.register(models.ProductsFieldValue)
