from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['phone_number', 'first_name', 'last_name', 'user_type', 'family_code', 'is_active']
    list_filter = ['user_type', 'is_active', 'created_at']
    search_fields = ['phone_number', 'first_name', 'last_name', 'family_code']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'date_of_birth', 'avatar')}),
        ('Family', {'fields': ('user_type', 'family_code')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'user_type', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
