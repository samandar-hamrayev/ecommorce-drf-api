from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import Category, Brand, Product, ProductField, ProductsFieldValue
from .serializers import CategoryDetailSerializer, ProductDetailSerializer

User = get_user_model()


class SimpleModelTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Admin va oddiy foydalanuvchini yaratamiz
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            password="admin123",
            first_name="Admin",
            last_name="User"
        )
        self.user = User.objects.create_user(
            email="user@example.com",
            password="user123",
            first_name="Regular",
            last_name="User"
        )
        self.client.force_authenticate(self.admin)

        # Test uchun Category yaratish
        self.category = Category.objects.create(
            name="Electronics",
            description="Gadgets and devices",
            created_by=self.admin
        )
        # Test uchun Brand yaratish
        self.brand = Brand.objects.create(
            name="TechBrand",
            description="Leading tech company",
            created_by=self.admin
        )
        # Test uchun Product yaratish
        self.product = Product.objects.create(
            name="Smartphone",
            category=self.category,
            brand=self.brand,
            created_by=self.admin,
            description="Latest model",
            price=Decimal("599.99"),
            stock=100,
            discount=10
        )
        # Test uchun ProductField yaratish
        self.product_field = ProductField.objects.create(
            name="Color",
            field_type="choice",
            choices="Red,Blue,Black"
        )
        # Test uchun ProductsFieldValue yaratish
        self.field_value = ProductsFieldValue.objects.create(
            product=self.product,
            field=self.product_field,
            value="Blue"
        )

    def test_create_category_as_admin(self):
        data = {
            "name": "Clothing",
            "description": "Apparel and accessories"
        }
        response = self.client.post(reverse("category-list"), data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Category.objects.count(), 2)
        self.assertEqual(Category.objects.last().name, "Clothing")

    def test_list_categories(self):
        response = self.client.get(reverse("category-list"))
        self.assertEqual(response.status_code, 200)
        # Agar API da pagination yoqilgan boʻlsa, natija 'results' kalitida keladi
        if isinstance(response.data, dict) and "results" in response.data:
            items = response.data["results"]
        else:
            items = response.data
        self.assertTrue(any(item["name"] == "Electronics" for item in items))

    def test_retrieve_category_detail(self):
        response = self.client.get(reverse("category-detail", kwargs={"pk": self.category.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Electronics")
        self.assertEqual(response.data["description"], "Gadgets and devices")

    def test_update_category_as_owner(self):
        data = {"name": "Updated Electronics", "description": "Updated gadgets"}
        response = self.client.put(
            reverse("category-detail", kwargs={"pk": self.category.pk}), data
        )
        self.assertEqual(response.status_code, 200)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Updated Electronics")

    def test_create_product_as_admin(self):
        data = {
            "name": "Laptop",
            "category": self.category.pk,
            "brand": self.brand.pk,
            "description": "High-end laptop",
            "price": "999.99",
            "stock": 50,
            "discount": 5
        }
        response = self.client.post(reverse("product-list"), data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.count(), 2)
        self.assertEqual(Product.objects.last().name, "Laptop")

    def test_product_discounted_price(self):
        response = self.client.get(reverse("product-detail", kwargs={"pk": self.product.pk}))
        self.assertEqual(response.status_code, 200)
        # Agar discount hisoblash natijasi integer bo'lsa
        self.assertEqual(response.data["discounted_price"], 540)

    def test_non_admin_cannot_create_category(self):
        # Foydalanuvchini admin emas holatga o’tkazamiz
        self.client.force_authenticate(self.user)
        data = {"name": "Books", "description": "Literature"}
        response = self.client.post(reverse("category-list"), data)
        self.assertEqual(response.status_code, 403)
        # Avval yaratilgan kategoriya soni 1 ekanligini tasdiqlaymiz
        self.assertEqual(Category.objects.count(), 1)

    def test_create_product_field(self):
        data = {"name": "Size", "field_type": "text"}
        response = self.client.post(reverse("field-list"), data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ProductField.objects.count(), 2)
        self.assertEqual(ProductField.objects.last().name, "Size")

    def test_create_field_value(self):
        # unique_together cheklovi sababli yangi maydon qo'shamiz
        new_field = ProductField.objects.create(
            name="Size",
            field_type="text"
        )
        data = {"field": new_field.pk, "value": "Large"}
        response = self.client.post(
            reverse("category-product-field-values-list",
                    kwargs={"category_pk": self.category.pk, "product_pk": self.product.pk}),
            data
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ProductsFieldValue.objects.count(), 2)
        self.assertEqual(ProductsFieldValue.objects.last().value, "Large")

    def test_user_full_name(self):
        self.assertEqual(self.user.full_name, "Regular User")
        self.assertEqual(self.admin.full_name, "Admin User")

    def test_product_average_rating_no_reviews(self):
        response = self.client.get(reverse("product-detail", kwargs={"pk": self.product.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["average_rating"], 0)

    def test_category_products_relation(self):
        response = self.client.get(reverse("category-detail", kwargs={"pk": self.category.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["products"]), 1)
        self.assertEqual(response.data["products"][0]["name"], "Smartphone")

    def test_non_owner_cannot_update_product(self):
        self.client.force_authenticate(self.user)
        data = {"name": "Updated Smartphone", "description": "Updated description"}
        response = self.client.patch(
            reverse("product-detail", kwargs={"pk": self.product.pk}), data
        )
        self.assertEqual(response.status_code, 403)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Smartphone")
