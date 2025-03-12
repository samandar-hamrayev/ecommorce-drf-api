from django.contrib import admin

from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'is_active','is_staff', 'is_superuser', 'gender')

admin.site.register(User, UserAdmin)
