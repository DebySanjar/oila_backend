from rest_framework import serializers
from django.utils import timezone
from .models import Task, Reward, RewardClaim, UserPoints, ChatMessage, ChatReadReceipt


class TaskSerializer(serializers.ModelSerializer):
    """Task serializer"""
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.get_full_name', read_only=True)
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'family_code', 'title', 'description',
            'assigned_to', 'assigned_to_name',
            'created_by', 'created_by_name',
            'status', 'priority',
            'reward_points', 'reward_screen_time_minutes',
            'due_date', 'completed_at', 'verified_at',
            'verified_by', 'verified_by_name',
            'is_overdue', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'family_code', 'created_by', 'created_by_name',
            'completed_at', 'verified_at', 'verified_by', 'verified_by_name',
            'is_overdue', 'created_at', 'updated_at'
        ]
    
    def get_is_overdue(self, obj):
        if obj.due_date and obj.status not in ['completed', 'verified']:
            return timezone.now() > obj.due_date
        return False
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        validated_data['family_code'] = self.context['request'].user.family_code
        return super().create(validated_data)


class TaskUpdateSerializer(serializers.ModelSerializer):
    """Task update serializer (for status changes)"""
    class Meta:
        model = Task
        fields = ['status']
    
    def validate_status(self, value):
        user = self.context['request'].user
        current_status = self.instance.status
        
        # Children can only mark as in_progress or completed
        if user.user_type == 'child':
            if value not in ['in_progress', 'completed']:
                raise serializers.ValidationError(
                    "Farzandlar faqat 'Bajarilmoqda' yoki 'Bajarildi' holatiga o'zgartirishi mumkin"
                )
        
        # Parents can verify or reject
        if user.user_type == 'parent':
            if value not in ['verified', 'rejected', 'pending']:
                raise serializers.ValidationError(
                    "Ota-onalar faqat tasdiqlashi yoki rad etishi mumkin"
                )
        
        return value
    
    def update(self, instance, validated_data):
        status = validated_data.get('status')
        user = self.context['request'].user
        
        if status == 'completed':
            instance.completed_at = timezone.now()
        elif status == 'verified':
            instance.verified_at = timezone.now()
            instance.verified_by = user
        
        return super().update(instance, validated_data)


class RewardSerializer(serializers.ModelSerializer):
    """Reward serializer"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Reward
        fields = [
            'id', 'family_code', 'title', 'description',
            'points_required', 'screen_time_minutes',
            'is_active', 'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'family_code', 'created_by', 'created_by_name', 'created_at']
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        validated_data['family_code'] = self.context['request'].user.family_code
        return super().create(validated_data)


class RewardClaimSerializer(serializers.ModelSerializer):
    """Reward claim serializer"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    reward_title = serializers.CharField(source='reward.title', read_only=True)
    reward_points = serializers.IntegerField(source='reward.points_required', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = RewardClaim
        fields = [
            'id', 'user', 'user_name',
            'reward', 'reward_title', 'reward_points',
            'status', 'approved_by', 'approved_by_name',
            'claimed_at', 'approved_at', 'redeemed_at'
        ]
        read_only_fields = [
            'id', 'user', 'user_name', 'reward_title', 'reward_points',
            'approved_by', 'approved_by_name',
            'claimed_at', 'approved_at', 'redeemed_at'
        ]
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class RewardClaimUpdateSerializer(serializers.ModelSerializer):
    """Reward claim update serializer (for approval)"""
    class Meta:
        model = RewardClaim
        fields = ['status']
    
    def validate_status(self, value):
        if value not in ['approved', 'rejected', 'redeemed']:
            raise serializers.ValidationError("Noto'g'ri holat")
        return value
    
    def update(self, instance, validated_data):
        status = validated_data.get('status')
        user = self.context['request'].user
        
        if status in ['approved', 'rejected']:
            instance.approved_at = timezone.now()
            instance.approved_by = user
        elif status == 'redeemed':
            instance.redeemed_at = timezone.now()
        
        return super().update(instance, validated_data)


class UserPointsSerializer(serializers.ModelSerializer):
    """User points serializer"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = UserPoints
        fields = [
            'id', 'user', 'user_name',
            'total_points', 'available_points', 'spent_points',
            'updated_at'
        ]
        read_only_fields = ['id', 'user', 'user_name', 'updated_at']


class ChatMessageSerializer(serializers.ModelSerializer):
    """Chat message serializer"""
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    sender_type = serializers.CharField(source='sender.user_type', read_only=True)
    sender_avatar = serializers.CharField(source='sender.avatar', read_only=True)
    reply_to_content = serializers.CharField(source='reply_to.content', read_only=True)
    read_by = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = [
            'id', 'family_code', 'sender', 'sender_name', 'sender_type',
            'sender_avatar', 'message_type', 'content', 'file',
            'latitude', 'longitude',
            'reply_to', 'reply_to_content',
            'is_edited', 'is_deleted',
            'read_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'family_code', 'sender', 'sender_name', 'sender_type',
            'sender_avatar', 'is_edited', 'is_deleted', 'read_by', 'created_at', 'updated_at'
        ]
    
    def get_read_by(self, obj):
        receipts = obj.read_receipts.select_related('user').all()
        return [
            {
                'user_id': r.user.id,
                'user_name': r.user.get_full_name(),
                'read_at': r.read_at
            }
            for r in receipts
        ]
    
    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        validated_data['family_code'] = self.context['request'].user.family_code
        return super().create(validated_data)


class ChatMessageCreateSerializer(serializers.ModelSerializer):
    """Chat message create serializer"""
    class Meta:
        model = ChatMessage
        fields = [
            'message_type', 'content', 'file',
            'latitude', 'longitude', 'reply_to'
        ]
    
    def validate(self, data):
        message_type = data.get('message_type', 'text')
        
        if message_type == 'text' and not data.get('content'):
            raise serializers.ValidationError("Matn xabarlari uchun content majburiy")
        
        if message_type in ['image', 'audio'] and not data.get('file'):
            raise serializers.ValidationError("Fayl xabarlari uchun file majburiy")
        
        if message_type == 'location' and (not data.get('latitude') or not data.get('longitude')):
            raise serializers.ValidationError("Joylashuv xabarlari uchun latitude va longitude majburiy")
        
        return data
    
    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        validated_data['family_code'] = self.context['request'].user.family_code
        return super().create(validated_data)


class ChatReadReceiptSerializer(serializers.ModelSerializer):
    """Chat read receipt serializer"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = ChatReadReceipt
        fields = ['id', 'message', 'user', 'user_name', 'read_at']
        read_only_fields = ['id', 'user', 'user_name', 'read_at']
