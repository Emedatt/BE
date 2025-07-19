from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, PhoneNumber, Staff

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'email_verified', 'created_at')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    readonly_fields = ('id', 'created_at', 'updated_at', 'email_verification_sent_at')
    ordering = ('-created_at',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('username', 'first_name', 'last_name', 'address')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Email Verification', {'fields': ('email_verified', 'email_verification_token', 'email_verification_sent_at')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )

@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ('number', 'user', 'type', 'is_primary', 'created_at')
    list_filter = ('type', 'is_primary', 'created_at')
    search_fields = ('number', 'user__email', 'user__username')
    readonly_fields = ('id', 'created_at', 'updated_at')
    raw_id_fields = ('user',)
    ordering = ('-is_primary', 'type')

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__email', 'user__username',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    raw_id_fields = ('user',)
    ordering = ('-created_at',)
