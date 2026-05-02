from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
import string
import random

User = get_user_model()


class Family(models.Model):
    """Family/Oila model"""
    family_code = models.CharField(max_length=6, unique=True, db_index=True)
    family_name = models.CharField(max_length=200, help_text="Oila nomi/tahallusi")
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_families'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'families'
        ordering = ['-created_at']
        verbose_name = 'Oila'
        verbose_name_plural = 'Oilalar'
    
    def __str__(self):
        return f"{self.family_name} ({self.family_code})"
    
    @staticmethod
    def generate_family_code():
        """Generate unique 6-character family code"""
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not Family.objects.filter(family_code=code).exists():
                return code
    
    def get_members(self):
        """Get all family members"""
        return User.objects.filter(family_code=self.family_code)
    
    def get_parents(self):
        """Get all parents in family"""
        return self.get_members().filter(user_type__in=['father', 'mother', 'grandfather', 'grandmother'])
    
    def get_children(self):
        """Get all children in family"""
        return self.get_members().filter(user_type__in=['son', 'daughter'])


class Task(models.Model):
    """Family tasks"""
    STATUS_CHOICES = (
        ('pending', 'Kutilmoqda'),
        ('in_progress', 'Bajarilmoqda'),
        ('completed', 'Bajarildi'),
        ('verified', 'Tasdiqlandi'),
        ('rejected', 'Rad etildi'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Past'),
        ('medium', 'O\'rta'),
        ('high', 'Yuqori'),
    )
    
    family_code = models.CharField(max_length=6, db_index=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_tasks'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tasks'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    reward_points = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    reward_screen_time_minutes = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Qo'shimcha ekran vaqti (daqiqalarda)"
    )
    due_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_tasks'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tasks'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['family_code', '-created_at']),
            models.Index(fields=['assigned_to', 'status']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.assigned_to.get_full_name()}"


class Reward(models.Model):
    """Rewards catalog"""
    family_code = models.CharField(max_length=6, db_index=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    points_required = models.IntegerField(validators=[MinValueValidator(0)])
    screen_time_minutes = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_rewards'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'rewards'
        ordering = ['points_required']
    
    def __str__(self):
        return f"{self.title} ({self.points_required} points)"


class RewardClaim(models.Model):
    """Claimed rewards"""
    STATUS_CHOICES = (
        ('pending', 'Kutilmoqda'),
        ('approved', 'Tasdiqlandi'),
        ('rejected', 'Rad etildi'),
        ('redeemed', 'Berildi'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reward_claims')
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE, related_name='claims')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_claims'
    )
    claimed_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    redeemed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'reward_claims'
        ordering = ['-claimed_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.reward.title}"


class UserPoints(models.Model):
    """User points balance"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='points')
    total_points = models.IntegerField(default=0)
    available_points = models.IntegerField(default=0)
    spent_points = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_points'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.available_points} points"


class ChatMessage(models.Model):
    """Family chat messages"""
    MESSAGE_TYPE_CHOICES = (
        ('text', 'Matn'),
        ('image', 'Rasm'),
        ('audio', 'Audio'),
        ('location', 'Joylashuv'),
    )
    
    family_code = models.CharField(max_length=6, db_index=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES, default='text')
    content = models.TextField(blank=True)
    file = models.FileField(upload_to='chat/', null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    reply_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies'
    )
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['family_code', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.sender.get_full_name()}: {self.content[:50]}"


class ChatReadReceipt(models.Model):
    """Message read receipts"""
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='read_receipts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='read_messages')
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_read_receipts'
        unique_together = ['message', 'user']
    
    def __str__(self):
        return f"{self.user.get_full_name()} read message {self.message.id}"
