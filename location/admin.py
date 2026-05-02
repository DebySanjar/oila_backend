from django.contrib import admin
from .models import Location, SafeZone, ZoneEvent


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['user', 'latitude', 'longitude', 'battery_level', 'timestamp']
    list_filter = ['timestamp', 'is_charging']
    search_fields = ['user__phone_number', 'user__first_name', 'user__last_name']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'


@admin.register(SafeZone)
class SafeZoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'zone_type', 'family_code', 'radius', 'is_active', 'created_at']
    list_filter = ['zone_type', 'is_active', 'created_at']
    search_fields = ['name', 'family_code']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ZoneEvent)
class ZoneEventAdmin(admin.ModelAdmin):
    list_display = ['user', 'zone', 'event_type', 'timestamp', 'notified']
    list_filter = ['event_type', 'notified', 'timestamp']
    search_fields = ['user__phone_number', 'zone__name']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
