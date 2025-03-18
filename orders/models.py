from django.db import models
from django.core.validators import MinValueValidator
from carts.models import Basket
from products.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    basket = models.ForeignKey(Basket, on_delete=models.SET_NULL, null=True, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    delivered_at = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} by {self.basket.user.email}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.total_price = self.basket.total_price
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')

    #freezing
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    discount = models.PositiveIntegerField(blank=True, null=True)
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.price_at_order = self.product.price
        super().save(*args, **kwargs)

    @property
    def total_price(self):
        return self.price_at_order * self.quantity