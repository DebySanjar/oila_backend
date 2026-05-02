from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Task, RewardClaim, UserPoints

User = get_user_model()


@receiver(post_save, sender=Task)
def handle_task_verification(sender, instance, created, **kwargs):
    """
    Handle task verification and award points
    
    Vazifa tasdiqlanganda ball berish
    """
    if not created and instance.status == 'verified':
        # Check if points already awarded
        if instance.reward_points > 0:
            # Get or create user points
            user_points, created = UserPoints.objects.get_or_create(
                user=instance.assigned_to
            )
            
            # Award points
            user_points.total_points += instance.reward_points
            user_points.available_points += instance.reward_points
            user_points.save()
            
            # TODO: Send notification to child
            # TODO: Log points transaction


@receiver(post_save, sender=RewardClaim)
def handle_reward_claim_approval(sender, instance, created, **kwargs):
    """
    Handle reward claim approval and deduct points
    
    Mukofot tasdiqlanganda ballni yechish
    """
    if not created and instance.status == 'approved':
        try:
            user_points = UserPoints.objects.get(user=instance.user)
            reward_points = instance.reward.points_required
            
            # Deduct points
            if user_points.available_points >= reward_points:
                user_points.available_points -= reward_points
                user_points.spent_points += reward_points
                user_points.save()
                
                # TODO: Send notification to child
                # TODO: Log points transaction
        except UserPoints.DoesNotExist:
            pass


@receiver(post_save, sender=User)
def create_user_points(sender, instance, created, **kwargs):
    """
    Create user points when user is created
    
    Foydalanuvchi yaratilganda ball hisobini yaratish
    """
    if created:
        UserPoints.objects.get_or_create(user=instance)
