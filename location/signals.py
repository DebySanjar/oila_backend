"""
Signals for location app
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ZoneEvent


@receiver(post_save, sender=ZoneEvent)
def notify_on_zone_event(sender, instance, created, **kwargs):
    """
    Send notification when zone event occurs
    """
    if created and not instance.notified:
        # TODO: Implement actual notification
        # This is where you would send push notification, SMS, etc.
        
        event_text = "kirdi" if instance.event_type == 'enter' else "chiqdi"
        message = f"{instance.user.get_full_name()} {instance.zone.name} ga {event_text}"
        
        print(f"[NOTIFICATION] {message}")
        
        # Mark as notified
        instance.notified = True
        instance.save(update_fields=['notified'])
