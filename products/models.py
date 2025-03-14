from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_categories')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    logo = models.ImageField(upload_to='images/brand-logos')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_brands')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='images/product-images/')
    alt_text = models.TextField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.product.name}"


class ProductField(models.Model):
    name = models.CharField(max_length=100)
    field_type = models.CharField(max_length=20, choices=[('text', 'Text'), ('number', 'Number'), ('choice', 'Choice'),])
    choices = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class ProductsFieldValue(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='field_values')
    field = models.ForeignKey(ProductField, on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.product.name} - {self.field.name}: {self.value}"

    class Meta:
        unique_together = ('product', 'field')



class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='created_products')
    description = models.TextField()
    price = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField(default=0)
    discount = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(90), MinValueValidator(0)])
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return round(sum(rating.value for rating in ratings) / ratings.count(), 2)
        return 0









