"""
Signals for accounts app
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(pre_save, sender=User)
def generate_family_code_for_parent(sender, instance, **kwargs):
    """
    Automatically generate family code for parent users
    """
    if instance.user_type == 'parent' and not instance.family_code:
        from .models import generate_family_code
        instance.family_code = generate_family_code()


@receiver(post_save, sender=User)
def user_created(sender, instance, created, **kwargs):
    """
    Actions to perform when a user is created
    """
    if created:
        # Log user creation
        print(f"New user created: {instance.phone_number} ({instance.get_user_type_display()})")
        
        # You can add more actions here:
        # - Send welcome email/SMS
        # - Create user profile
        # - Send notification to family members
        # - etc.


@receiver(post_save, sender=User)
def notify_family_on_child_join(sender, instance, created, **kwargs):
    """
    Notify family members when a child joins
    """
    if created and instance.user_type == 'child' and instance.family_code:
        # Get all family members
        family_members = User.objects.filter(
            family_code=instance.family_code,
            user_type='parent'
        ).exclude(id=instance.id)
        
        for member in family_members:
            # Here you can send notification
            print(f"Notify {member.phone_number}: New child {instance.get_full_name()} joined the family")
            # TODO: Implement actual notification (push, SMS, etc.)
