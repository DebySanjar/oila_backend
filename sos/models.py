from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class SOSAlert(models.Model):
    """SOS emergency alerts"""
    STATUS_CHOICES = (
        ('active', 'Faol'),
        ('acknowledged', 'Ko\'rildi'),
        ('resolved', 'Hal qilindi'),
        ('false_alarm', 'Noto\'g\'ri signal'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sos_alerts')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', db_index=True)
    message = models.TextField(blank=True, help_text="Optional message from user")
    audio_file = models.FileField(upload_to='sos/audio/', null=True, blank=True)
    battery_level = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='acknowledged_sos'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_sos'
    )
    notes = models.TextField(blank=True, help_text="Notes from parents")
    
    class Meta:
        db_table = 'sos_alerts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"SOS from {self.user.phone_number} - {self.get_status_display()}"


class SOSContact(models.Model):
    """Emergency contacts for SOS"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sos_contacts')
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    relationship = models.CharField(max_length=50, help_text="Relationship to user")
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'sos_contacts'
        ordering = ['-is_primary', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.phone_number})"
