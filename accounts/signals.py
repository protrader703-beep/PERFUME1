"""
accounts/signals.py

Django signals let us run code automatically when certain events happen.

Here we use the 'post_save' signal on the User model:
- When a NEW User is created → auto-create their UserProfile
- When an EXISTING User is saved → save their existing UserProfile

This means: every User always has a UserProfile, automatically.
"""

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a UserProfile when a new User is registered."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile whenever the User object is saved."""
    instance.userprofile.save()
