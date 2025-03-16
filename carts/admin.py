from django.contrib import admin
from . import models



@admin.register(models.Basket)
class BasketAdmin(admin.ModelAdmin):
    model = models.Basket
    list_display = [field.name for field in models.Basket._meta.fields]

@admin.register(models.BasketItem)
class BasketItemAdmin(admin.ModelAdmin):
    model = models.BasketItem
    list_display = [field.name for field in models.BasketItem._meta.fields]