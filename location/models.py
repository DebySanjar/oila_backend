from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Location(models.Model):
    """Real-time location tracking"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='locations')
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6,
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6,
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    accuracy = models.FloatField(help_text="Accuracy in meters", null=True, blank=True)
    altitude = models.FloatField(null=True, blank=True)
    speed = models.FloatField(null=True, blank=True, help_text="Speed in m/s")
    heading = models.FloatField(null=True, blank=True, help_text="Direction in degrees")
    battery_level = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    is_charging = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'locations'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.phone_number} - {self.timestamp}"


class SafeZone(models.Model):
    """Safe zones (Xavfsiz hududlar)"""
    ZONE_TYPE_CHOICES = (
        ('home', 'Uy'),
        ('school', 'Maktab'),
        ('relative', 'Qarindosh uyi'),
        ('other', 'Boshqa'),
    )
    
    family_code = models.CharField(max_length=6, db_index=True)
    name = models.CharField(max_length=100)
    zone_type = models.CharField(max_length=20, choices=ZONE_TYPE_CHOICES, default='other')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    radius = models.IntegerField(help_text="Radius in meters", default=100)
    is_active = models.BooleanField(default=True)
    notify_on_enter = models.BooleanField(default=True)
    notify_on_exit = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_zones')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'safe_zones'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_zone_type_display()})"


class ZoneEvent(models.Model):
    """Zone entry/exit events"""
    EVENT_TYPE_CHOICES = (
        ('enter', 'Kirdi'),
        ('exit', 'Chiqdi'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='zone_events')
    zone = models.ForeignKey(SafeZone, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=10, choices=EVENT_TYPE_CHOICES)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    notified = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'zone_events'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['zone', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.phone_number} {self.get_event_type_display()} {self.zone.name}"
