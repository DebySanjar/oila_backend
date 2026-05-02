from django.contrib import admin
from .models import Task, Reward, RewardClaim, UserPoints, ChatMessage, ChatReadReceipt


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Task admin"""
    list_display = [
        'title', 'assigned_to', 'status', 'priority',
        'reward_points', 'reward_screen_time_minutes',
        'due_date', 'created_by', 'created_at'
    ]
    list_filter = ['status', 'priority', 'created_at', 'due_date']
    search_fields = [
        'title', 'description',
        'assigned_to__phone_number', 'assigned_to__first_name',
        'created_by__phone_number', 'created_by__first_name'
    ]
    readonly_fields = ['completed_at', 'verified_at', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Vazifa', {
            'fields': ('title', 'description', 'family_code')
        }),
        ('Tayinlash', {
            'fields': ('assigned_to', 'created_by')
        }),
        ('Holat', {
            'fields': ('status', 'priority')
        }),
        ('Mukofot', {
            'fields': ('reward_points', 'reward_screen_time_minutes')
        }),
        ('Vaqt', {
            'fields': ('due_date', 'completed_at', 'verified_at', 'verified_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    """Reward admin"""
    list_display = [
        'title', 'points_required', 'screen_time_minutes',
        'is_active', 'family_code', 'created_by', 'created_at'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description', 'family_code']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Mukofot', {
            'fields': ('title', 'description', 'family_code')
        }),
        ('Narx', {
            'fields': ('points_required', 'screen_time_minutes')
        }),
        ('Holat', {
            'fields': ('is_active', 'created_by', 'created_at')
        }),
    )


@admin.register(RewardClaim)
class RewardClaimAdmin(admin.ModelAdmin):
    """Reward claim admin"""
    list_display = [
        'user', 'reward', 'status',
        'claimed_at', 'approved_by', 'approved_at'
    ]
    list_filter = ['status', 'claimed_at', 'approved_at']
    search_fields = [
        'user__phone_number', 'user__first_name',
        'reward__title'
    ]
    readonly_fields = ['claimed_at', 'approved_at', 'redeemed_at']
    date_hierarchy = 'claimed_at'
    
    fieldsets = (
        ('So\'rov', {
            'fields': ('user', 'reward', 'status')
        }),
        ('Tasdiqlash', {
            'fields': ('approved_by', 'approved_at', 'redeemed_at')
        }),
        ('Vaqt', {
            'fields': ('claimed_at',)
        }),
    )


@admin.register(UserPoints)
class UserPointsAdmin(admin.ModelAdmin):
    """User points admin"""
    list_display = [
        'user', 'total_points', 'available_points',
        'spent_points', 'updated_at'
    ]
    search_fields = ['user__phone_number', 'user__first_name', 'user__last_name']
    readonly_fields = ['updated_at']
    
    fieldsets = (
        ('Foydalanuvchi', {
            'fields': ('user',)
        }),
        ('Ballar', {
            'fields': ('total_points', 'available_points', 'spent_points')
        }),
        ('Vaqt', {
            'fields': ('updated_at',)
        }),
    )


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """Chat message admin"""
    list_display = [
        'sender', 'message_type', 'get_content_preview',
        'is_edited', 'is_deleted', 'created_at'
    ]
    list_filter = ['message_type', 'is_edited', 'is_deleted', 'created_at']
    search_fields = [
        'sender__phone_number', 'sender__first_name',
        'content', 'family_code'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Xabar', {
            'fields': ('family_code', 'sender', 'message_type')
        }),
        ('Kontent', {
            'fields': ('content', 'file', 'latitude', 'longitude')
        }),
        ('Javob', {
            'fields': ('reply_to',)
        }),
        ('Holat', {
            'fields': ('is_edited', 'is_deleted')
        }),
        ('Vaqt', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_content_preview(self, obj):
        if obj.content:
            return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
        return f"[{obj.get_message_type_display()}]"
    get_content_preview.short_description = 'Kontent'


@admin.register(ChatReadReceipt)
class ChatReadReceiptAdmin(admin.ModelAdmin):
    """Chat read receipt admin"""
    list_display = ['message', 'user', 'read_at']
    list_filter = ['read_at']
    search_fields = ['user__phone_number', 'user__first_name']
    readonly_fields = ['read_at']
    date_hierarchy = 'read_at'
    
    fieldsets = (
        ('O\'qilgan', {
            'fields': ('message', 'user', 'read_at')
        }),
    )
