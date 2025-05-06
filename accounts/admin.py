from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'api_key']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('location', 'age', 'api_key')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('location', 'age')}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
