from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class ScreenTimeRule(models.Model):
    """Screen time rules for children"""
    DAY_CHOICES = (
        ('monday', 'Dushanba'),
        ('tuesday', 'Seshanba'),
        ('wednesday', 'Chorshanba'),
        ('thursday', 'Payshanba'),
        ('friday', 'Juma'),
        ('saturday', 'Shanba'),
        ('sunday', 'Yakshanba'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='screen_time_rules')
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField(help_text="Ruxsat berilgan vaqt boshlanishi")
    end_time = models.TimeField(help_text="Ruxsat berilgan vaqt tugashi")
    max_duration_minutes = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(1440)],
        help_text="Maksimal foydalanish vaqti (daqiqalarda)"
    )
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_screen_rules'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'screen_time_rules'
        unique_together = ['user', 'day_of_week']
    
    def __str__(self):
        return f"{self.user.phone_number} - {self.get_day_of_week_display()}"


class AppUsage(models.Model):
    """Track app usage"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='app_usage')
    app_name = models.CharField(max_length=200)
    package_name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, blank=True)
    duration_seconds = models.IntegerField(validators=[MinValueValidator(0)])
    date = models.DateField(db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'app_usage'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.user.phone_number} - {self.app_name} ({self.duration_seconds}s)"


class BlockedApp(models.Model):
    """Blocked applications"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_apps')
    app_name = models.CharField(max_length=200)
    package_name = models.CharField(max_length=200)
    reason = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    blocked_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='apps_blocked'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'blocked_apps'
        unique_together = ['user', 'package_name']
    
    def __str__(self):
        return f"{self.app_name} - {self.user.phone_number}"


class ContentFilter(models.Model):
    """Content filtering rules"""
    FILTER_TYPE_CHOICES = (
        ('website', 'Veb-sayt'),
        ('keyword', 'Kalit so\'z'),
        ('category', 'Kategoriya'),
    )
    
    CATEGORY_CHOICES = (
        ('adult', 'Kattalar uchun'),
        ('violence', 'Zo\'ravonlik'),
        ('gambling', 'Qimor'),
        ('drugs', 'Giyohvand moddalar'),
        ('weapons', 'Qurol'),
        ('hate', 'Nafrat'),
        ('other', 'Boshqa'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='content_filters')
    filter_type = models.CharField(max_length=20, choices=FILTER_TYPE_CHOICES)
    value = models.CharField(max_length=500, help_text="URL, keyword, or category")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='filters_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'content_filters'
    
    def __str__(self):
        return f"{self.get_filter_type_display()}: {self.value}"


class BlockedContent(models.Model):
    """Log of blocked content attempts"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_content')
    content_type = models.CharField(max_length=20)
    url = models.URLField(max_length=1000, blank=True)
    app_name = models.CharField(max_length=200, blank=True)
    reason = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'blocked_content'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.phone_number} - {self.content_type} blocked"


class ScreenTimeSession(models.Model):
    """Track screen time sessions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='screen_sessions')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    device_info = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'screen_time_sessions'
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.user.phone_number} - {self.start_time}"
    
    def save(self, *args, **kwargs):
        if self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            self.duration_seconds = int(delta.total_seconds())
        super().save(*args, **kwargs)
