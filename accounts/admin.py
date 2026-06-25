"""
accounts/admin.py

Register the UserProfile model in the admin panel.
The shop owner can view customer profiles from the admin.
"""

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    """Show UserProfile fields directly inside the User detail page in admin."""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Customer Profile'


class UserAdmin(BaseUserAdmin):
    """Extend the default User admin to include the profile inline."""
    inlines = [UserProfileInline]


# Re-register User with our custom admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Also register UserProfile separately so it can be viewed standalone
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city', 'state', 'pincode']
    search_fields = ['user__username', 'user__email', 'phone', 'city']
    list_filter = ['state']
