from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile

@receiver(post_save, sender=User)
def create_profile_for_user(sender, instance, created, **kwargs):
    """Create a default participant profile on user creation if missing."""
    if created:
        UserProfile.objects.get_or_create(user=instance, defaults={'role': 'participant'})
