from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, UserProfileForm

def signup(request):
    if request.user.is_authenticated:
        return redirect('store:home')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to Attar Store, {user.username}!')
            return redirect('store:home')
    else:
        form = CustomUserCreationForm()
        
    context = {
        'form': form,
        'page_title': 'Create Account — Attar Store'
    }
    return render(request, 'accounts/signup.html', context)

def user_login(request):
    if request.user.is_authenticated:
        return redirect('store:home')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next', 'store:home')
                return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
        
    context = {
        'form': form,
        'page_title': 'Login — Attar Store'
    }
    return render(request, 'accounts/login.html', context)

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('store:home')

@login_required
def profile(request):
    # Get user profile created by the signal, or create if it doesn't exist (e.g. for superuser created early)
    from .models import UserProfile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            # If user updated name (first_name/last_name), save it to User model
            request.user.first_name = request.POST.get('first_name', '')
            request.user.last_name = request.POST.get('last_name', '')
            request.user.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=profile)
        
    orders = request.user.orders.all().order_by('-created_at')
    context = {
        'form': form,
        'orders': orders,
        'page_title': 'My Profile — Attar Store',
    }
    return render(request, 'accounts/profile.html', context)
