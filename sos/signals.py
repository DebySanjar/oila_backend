"""
Signals for SOS app
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import SOSAlert

User = get_user_model()


@receiver(post_save, sender=SOSAlert)
def notify_family_on_sos(sender, instance, created, **kwargs):
    """
    Notify all family members when SOS is triggered
    """
    if created:
        # Get all family members (parents)
        family_members = User.objects.filter(
            family_code=instance.user.family_code,
            user_type='parent'
        ).exclude(id=instance.user.id)
        
        for member in family_members:
            # TODO: Send push notification
            # TODO: Send SMS
            # TODO: Make phone call (if configured)
            
            print(f"[SOS ALERT] Notifying {member.phone_number} about SOS from {instance.user.get_full_name()}")
            print(f"  Location: {instance.latitude}, {instance.longitude}")
            print(f"  Battery: {instance.battery_level}%")
            print(f"  Message: {instance.message}")
