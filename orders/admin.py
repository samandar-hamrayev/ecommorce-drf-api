from django.contrib import admin

from . import models

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in models.Order._meta.fields]
    readonly_fields = ['total_price']


@admin.register(models.OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = [field.name for field in models.OrderItem._meta.fields]
