from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'phone', 'is_staff', 'is_active', 'created_at')
    list_filter = ('is_staff', 'is_active', 'created_at')
    search_fields = ('email', 'username', 'phone')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'last_login')

    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительные данные', {'fields': ('phone', 'created_at')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительные данные', {'fields': ('email', 'phone')}),
    )
