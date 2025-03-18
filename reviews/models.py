from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User
from products.models import Product

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    value = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=True, null=True
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.text and self.value:
            return f"Review by {self.user.email} on {self.product.name}: {self.value}/5 - {self.text[:20]}"
        elif self.text:
            return f"Comment by {self.user.email} on {self.product.name}: {self.text[:20]}"
        elif self.value:
            return f"Rating by {self.user.email} on {self.product.name}: {self.value}/5"
        return f"Review by {self.user.email} on {self.product.name}"

    class Meta:
        unique_together = ('user', 'product')