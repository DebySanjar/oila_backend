from django.contrib import admin
from .models import SOSAlert, SOSContact


@admin.register(SOSAlert)
class SOSAlertAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'battery_level', 'created_at', 'acknowledged_by', 'resolved_by']
    list_filter = ['status', 'created_at']
    search_fields = ['user__phone_number', 'user__first_name', 'user__last_name', 'message']
    readonly_fields = ['created_at', 'acknowledged_at', 'resolved_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Alert Info', {
            'fields': ('user', 'status', 'message', 'audio_file')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude', 'battery_level')
        }),
        ('Response', {
            'fields': ('acknowledged_at', 'acknowledged_by', 'resolved_at', 'resolved_by', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


@admin.register(SOSContact)
class SOSContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone_number', 'user', 'relationship', 'is_primary', 'is_active']
    list_filter = ['is_primary', 'is_active', 'created_at']
    search_fields = ['name', 'phone_number', 'user__phone_number']
    readonly_fields = ['created_at']
