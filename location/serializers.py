from rest_framework import serializers
from .models import Location, SafeZone, ZoneEvent
from accounts.serializers import UserSerializer


class LocationSerializer(serializers.ModelSerializer):
    """Location serializer"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Location
        fields = [
            'id', 'user', 'user_name', 'latitude', 'longitude', 
            'accuracy', 'altitude', 'speed', 'heading',
            'battery_level', 'is_charging', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp', 'user_name']


class LocationCreateSerializer(serializers.ModelSerializer):
    """Location create serializer"""
    class Meta:
        model = Location
        fields = [
            'latitude', 'longitude', 'accuracy', 'altitude', 
            'speed', 'heading', 'battery_level', 'is_charging'
        ]
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class SafeZoneSerializer(serializers.ModelSerializer):
    """Safe zone serializer"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = SafeZone
        fields = [
            'id', 'family_code', 'name', 'zone_type', 
            'latitude', 'longitude', 'radius', 'is_active',
            'notify_on_enter', 'notify_on_exit',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'family_code', 'created_by', 'created_by_name', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['family_code'] = user.family_code
        validated_data['created_by'] = user
        return super().create(validated_data)


class ZoneEventSerializer(serializers.ModelSerializer):
    """Zone event serializer"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    zone_name = serializers.CharField(source='zone.name', read_only=True)
    
    class Meta:
        model = ZoneEvent
        fields = [
            'id', 'user', 'user_name', 'zone', 'zone_name',
            'event_type', 'location', 'timestamp', 'notified'
        ]
        read_only_fields = ['id', 'timestamp', 'user_name', 'zone_name']


class LocationHistorySerializer(serializers.Serializer):
    """Location history query serializer"""
    user_id = serializers.IntegerField(required=False)
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
    limit = serializers.IntegerField(default=100, max_value=1000)
