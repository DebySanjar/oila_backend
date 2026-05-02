from django.contrib import admin
from .models import (
    ScreenTimeRule, AppUsage, BlockedApp,
    ContentFilter, BlockedContent, ScreenTimeSession
)


@admin.register(ScreenTimeRule)
class ScreenTimeRuleAdmin(admin.ModelAdmin):
    """Screen time rule admin"""
    list_display = ['user', 'day_of_week', 'start_time', 'end_time', 'max_duration_minutes', 'is_active', 'created_at']
    list_filter = ['day_of_week', 'is_active', 'created_at']
    search_fields = ['user__phone_number', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Foydalanuvchi', {
            'fields': ('user', 'created_by')
        }),
        ('Qoida', {
            'fields': ('day_of_week', 'start_time', 'end_time', 'max_duration_minutes', 'is_active')
        }),
        ('Vaqt', {
            'fields': ('created_at',)
        }),
    )


@admin.register(AppUsage)
class AppUsageAdmin(admin.ModelAdmin):
    """App usage admin"""
    list_display = ['user', 'app_name', 'package_name', 'category', 'duration_seconds', 'date', 'timestamp']
    list_filter = ['date', 'category', 'timestamp']
    search_fields = ['user__phone_number', 'app_name', 'package_name']
    readonly_fields = ['timestamp']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Foydalanuvchi', {
            'fields': ('user',)
        }),
        ('Ilova', {
            'fields': ('app_name', 'package_name', 'category')
        }),
        ('Foydalanish', {
            'fields': ('duration_seconds', 'date', 'timestamp')
        }),
    )


@admin.register(BlockedApp)
class BlockedAppAdmin(admin.ModelAdmin):
    """Blocked app admin"""
    list_display = ['user', 'app_name', 'package_name', 'is_active', 'blocked_by', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__phone_number', 'app_name', 'package_name']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Foydalanuvchi', {
            'fields': ('user', 'blocked_by')
        }),
        ('Ilova', {
            'fields': ('app_name', 'package_name', 'reason', 'is_active')
        }),
        ('Vaqt', {
            'fields': ('created_at',)
        }),
    )


@admin.register(ContentFilter)
class ContentFilterAdmin(admin.ModelAdmin):
    """Content filter admin"""
    list_display = ['user', 'filter_type', 'value', 'category', 'is_active', 'created_by', 'created_at']
    list_filter = ['filter_type', 'category', 'is_active', 'created_at']
    search_fields = ['user__phone_number', 'value']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Foydalanuvchi', {
            'fields': ('user', 'created_by')
        }),
        ('Filtr', {
            'fields': ('filter_type', 'value', 'category', 'is_active')
        }),
        ('Vaqt', {
            'fields': ('created_at',)
        }),
    )


@admin.register(BlockedContent)
class BlockedContentAdmin(admin.ModelAdmin):
    """Blocked content admin"""
    list_display = ['user', 'content_type', 'url', 'app_name', 'reason', 'timestamp']
    list_filter = ['content_type', 'timestamp']
    search_fields = ['user__phone_number', 'url', 'app_name', 'reason']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Foydalanuvchi', {
            'fields': ('user',)
        }),
        ('Kontent', {
            'fields': ('content_type', 'url', 'app_name', 'reason')
        }),
        ('Vaqt', {
            'fields': ('timestamp',)
        }),
    )


@admin.register(ScreenTimeSession)
class ScreenTimeSessionAdmin(admin.ModelAdmin):
    """Screen time session admin"""
    list_display = ['user', 'start_time', 'end_time', 'duration_seconds', 'get_duration_minutes']
    list_filter = ['start_time']
    search_fields = ['user__phone_number']
    readonly_fields = ['duration_seconds']
    date_hierarchy = 'start_time'
    
    fieldsets = (
        ('Foydalanuvchi', {
            'fields': ('user',)
        }),
        ('Sessiya', {
            'fields': ('start_time', 'end_time', 'duration_seconds', 'device_info')
        }),
    )
    
    def get_duration_minutes(self, obj):
        if obj.duration_seconds:
            return f"{obj.duration_seconds // 60} daqiqa"
        return "-"
    get_duration_minutes.short_description = 'Davomiyligi'
