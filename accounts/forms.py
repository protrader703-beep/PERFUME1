from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    """Extends standard creation form to require email."""
    email = forms.EmailField(required=True, help_text='Required for order updates and password resets.')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'address_line1', 'city', 'state', 'pincode']
