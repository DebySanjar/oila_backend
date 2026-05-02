from rest_framework import serializers
from .models import SOSAlert, SOSContact
from accounts.serializers import UserSerializer


class SOSAlertSerializer(serializers.ModelSerializer):
    """SOS Alert serializer"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_phone = serializers.CharField(source='user.phone_number', read_only=True)
    acknowledged_by_name = serializers.CharField(source='acknowledged_by.get_full_name', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.get_full_name', read_only=True)
    
    class Meta:
        model = SOSAlert
        fields = [
            'id', 'user', 'user_name', 'user_phone',
            'latitude', 'longitude', 'status', 'message',
            'audio_file', 'battery_level', 'created_at',
            'acknowledged_at', 'acknowledged_by', 'acknowledged_by_name',
            'resolved_at', 'resolved_by', 'resolved_by_name', 'notes'
        ]
        read_only_fields = [
            'id', 'user', 'user_name', 'user_phone', 'created_at',
            'acknowledged_at', 'acknowledged_by', 'acknowledged_by_name',
            'resolved_at', 'resolved_by', 'resolved_by_name'
        ]


class SOSAlertCreateSerializer(serializers.ModelSerializer):
    """SOS Alert create serializer"""
    class Meta:
        model = SOSAlert
        fields = ['latitude', 'longitude', 'message', 'audio_file', 'battery_level']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class SOSAlertUpdateSerializer(serializers.ModelSerializer):
    """SOS Alert update serializer (for parents)"""
    class Meta:
        model = SOSAlert
        fields = ['status', 'notes']
    
    def update(self, instance, validated_data):
        from django.utils import timezone
        
        user = self.context['request'].user
        new_status = validated_data.get('status')
        
        if new_status == 'acknowledged' and instance.status == 'active':
            instance.acknowledged_at = timezone.now()
            instance.acknowledged_by = user
        
        if new_status == 'resolved' and instance.status != 'resolved':
            instance.resolved_at = timezone.now()
            instance.resolved_by = user
        
        return super().update(instance, validated_data)


class SOSContactSerializer(serializers.ModelSerializer):
    """SOS Contact serializer"""
    class Meta:
        model = SOSContact
        fields = [
            'id', 'user', 'name', 'phone_number', 'relationship',
            'is_primary', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
