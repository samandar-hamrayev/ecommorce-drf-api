import os
from uuid import uuid4
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.timezone import now
from . import  utils


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=128, blank=True)
    last_name = models.CharField(max_length=128, blank=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')], blank=True)
    avatar = models.ImageField(upload_to='images/user-avatars/', null=True, blank=True)
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

class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_verification')
    code = models.CharField(max_length=6, default=utils.generate_verification_code)
    created = models.DateTimeField(auto_now_add=True)
    expires = models.DateTimeField(default=utils.get_expiry_time)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.is_used and now() < self.expires