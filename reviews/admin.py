from django.contrib import admin
from . import models

@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [field.name for field in models.Review._meta.fields]
