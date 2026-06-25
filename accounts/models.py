"""
accounts/models.py

UserProfile extends Django's built-in User model.

Django provides authentication (username, password, email) for free.
UserProfile adds our business-specific fields: phone, saved address, etc.

The 'signals.py' file will auto-create a UserProfile whenever a new 
User is created via Django's signal system.
"""

from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """
    Extends the built-in Django User with additional customer information.
    
    This is a "One-to-One" relationship: every User has exactly one Profile.
    Access it in code via: request.user.userprofile
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,  # Delete profile if user is deleted
        related_name='userprofile',
        verbose_name="User Account"
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        verbose_name="Phone Number"
    )

    # Saved Shipping Address (auto-fills on checkout for convenience)
    address_line1 = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Address Line 1"
    )
    address_line2 = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Address Line 2"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="City"
    )
    state = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="State"
    )
    pincode = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="PIN Code"
    )

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"Profile of {self.user.username}"

    def get_full_address(self):
        """Returns the saved address as a single formatted string."""
        parts = [
            self.address_line1,
            self.address_line2,
            self.city,
            self.state,
            self.pincode,
        ]
        return ', '.join(part for part in parts if part)
