"""Schools admin configuration"""
from django.contrib import admin
from .models import School, SchoolUser


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'subdomain', 'status', 'subscription_active', 'created_at']
    list_filter = ['status', 'subscription_active', 'created_at']
    search_fields = ['name', 'subdomain', 'email']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'subdomain', 'email', 'phone', 'address')
        }),
        ('Branding', {
            'fields': ('logo', 'theme_color', 'motto')
        }),
        ('Status', {
            'fields': ('status', 'is_demo', 'subscription_active', 'subscription_expires')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SchoolUser)
class SchoolUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'school', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'school']
    search_fields = ['user__username', 'user__email', 'school__name']
