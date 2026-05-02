from rest_framework import serializers
from .models import (
    ScreenTimeRule, AppUsage, BlockedApp,
    ContentFilter, BlockedContent, ScreenTimeSession
)


class ScreenTimeRuleSerializer(serializers.ModelSerializer):
    """Screen time rule serializer"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = ScreenTimeRule
        fields = [
            'id', 'user', 'day_of_week', 'start_time', 'end_time',
            'max_duration_minutes', 'is_active',
            'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_by_name', 'created_at']
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class AppUsageSerializer(serializers.ModelSerializer):
    """App usage serializer"""
    class Meta:
        model = AppUsage
        fields = [
            'id', 'user', 'app_name', 'package_name', 'category',
            'duration_seconds', 'date', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class BlockedAppSerializer(serializers.ModelSerializer):
    """Blocked app serializer"""
    blocked_by_name = serializers.CharField(source='blocked_by.get_full_name', read_only=True)
    
    class Meta:
        model = BlockedApp
        fields = [
            'id', 'user', 'app_name', 'package_name', 'reason',
            'is_active', 'blocked_by', 'blocked_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'blocked_by', 'blocked_by_name', 'created_at']
    
    def create(self, validated_data):
        validated_data['blocked_by'] = self.context['request'].user
        return super().create(validated_data)


class ContentFilterSerializer(serializers.ModelSerializer):
    """Content filter serializer"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = ContentFilter
        fields = [
            'id', 'user', 'filter_type', 'value', 'category',
            'is_active', 'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_by_name', 'created_at']
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class BlockedContentSerializer(serializers.ModelSerializer):
    """Blocked content serializer"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = BlockedContent
        fields = [
            'id', 'user', 'user_name', 'content_type', 'url',
            'app_name', 'reason', 'timestamp'
        ]
        read_only_fields = ['id', 'user', 'user_name', 'timestamp']


class ScreenTimeSessionSerializer(serializers.ModelSerializer):
    """Screen time session serializer"""
    class Meta:
        model = ScreenTimeSession
        fields = [
            'id', 'user', 'start_time', 'end_time',
            'duration_seconds', 'device_info'
        ]
        read_only_fields = ['id', 'duration_seconds']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ScreenTimeStatsSerializer(serializers.Serializer):
    """Screen time statistics"""
    total_duration_seconds = serializers.IntegerField()
    total_duration_minutes = serializers.IntegerField()
    total_duration_hours = serializers.FloatField()
    session_count = serializers.IntegerField()
    average_session_minutes = serializers.FloatField()
    most_used_apps = serializers.ListField()
    daily_breakdown = serializers.DictField()
