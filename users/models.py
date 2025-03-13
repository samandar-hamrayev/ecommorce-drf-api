import os.path
import random
from uuid import uuid4
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.timezone import now
from datetime import timedelta

from rest_framework.exceptions import ValidationError


def user_avatar_file_path(instance, filename):
    ext = str(filename).split(".")[-1]
    filename = f"user_{uuid4()}.{ext}"
    return os.path.join("user-avatars/", filename)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, phone_number, password, **extra_fields):
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)
        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValidationError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValidationError("Superuser must have is_superuser=True.")

        return self._create_user(phone_number, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=128, blank=True, help_text="Samandar")
    last_name = models.CharField(max_length=128, blank=True)
    email = models.EmailField(unique=True)

    gender = models.CharField(max_length=10, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
    ], blank=True)
    avatar = models.ImageField(upload_to=user_avatar_file_path, null=True, blank=True)

    born_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


def generate_verification_code():
    return f"{random.randint(100_000, 999_999)}"

def get_expiry_time():
    return now() + timedelta(minutes=10)

class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_verification')
    code = models.CharField(max_length=6, default=generate_verification_code)
    created = models.DateTimeField(auto_now_add=True)
    expires = models.DateTimeField(default=get_expiry_time)
    is_used = models.BooleanField(default=False)


    def is_valid(self):
        return not self.is_used and now() < self.expires

