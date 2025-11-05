from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from Upohar.models import User, UpoharPost, UpoharRequest, Category
from Upohar.forms import UpoharPostForm
from users.forms import UserProfileForm

# Template Views


@login_required
def dashboard(request):
    user = request.user
    context = {'user': user}
    
    if user.role == 'donor' or user.is_donor_user:
        posts = UpoharPost.objects.filter(donor=user).order_by('-created_at')
        requests = UpoharRequest.objects.filter(gift__donor=user).order_by('-created_at')
        
        # Statistics
        total_posts = posts.count()
        available_posts = posts.filter(status='available').count()
        requested_posts = posts.filter(status='requested').count()
        completed_posts = posts.filter(status='completed').count()
        pending_requests = requests.filter(status='pending').count()
        approved_requests = requests.filter(status='approved').count()
        
        context.update({
            'posts': posts[:5],  # Show only recent 5 posts
            'requests': requests[:5],  # Show only recent 5 requests
            'total_posts': total_posts,
            'available_posts': available_posts,
            'requested_posts': requested_posts,
            'completed_posts': completed_posts,
            'pending_requests': pending_requests,
            'approved_requests': approved_requests,
        })
        template = 'donor_dashboard.html'
        
    elif user.role == 'receiver':
        received_gifts = UpoharPost.objects.filter(receiver=user).order_by('-updated_at')
        requests = UpoharRequest.objects.filter(requester=user).order_by('-created_at')
        
        # Statistics
        total_received = received_gifts.count()
        pending_requests = requests.filter(status='pending').count()
        approved_requests = requests.filter(status='approved').count()
        rejected_requests = requests.filter(status='rejected').count()
        
        context.update({
            'received_gifts': received_gifts[:5],
            'requests': requests[:5],
            'total_received': total_received,
            'pending_requests': pending_requests,
            'approved_requests': approved_requests,
            'rejected_requests': rejected_requests,
        })
        template = 'receiver_dashboard.html'
        
    elif user.role == 'exchanger':
        posts = UpoharPost.objects.filter(donor=user).order_by('-created_at')
        requests_sent = UpoharRequest.objects.filter(requester=user).order_by('-created_at')
        requests_received = UpoharRequest.objects.filter(gift__donor=user).order_by('-created_at')
        
        # Statistics
        total_posts = posts.count()
        available_posts = posts.filter(status='available').count()
        sent_requests = requests_sent.count()
        pending_sent = requests_sent.filter(status='pending').count()
        received_requests = requests_received.count()
        pending_received = requests_received.filter(status='pending').count()
        
        context.update({
            'posts': posts[:5],
            'requests_sent': requests_sent[:5],
            'requests_received': requests_received[:5],
            'total_posts': total_posts,
            'available_posts': available_posts,
            'sent_requests': sent_requests,
            'pending_sent': pending_sent,
            'received_requests': received_requests,
            'pending_received': pending_received,
        })
        template = 'exchanger_dashboard.html'
    
    return render(request, template, context)


@login_required
def profile(request):
    user = request.user
    
    # Get user statistics
    user_stats = {
        'posts_created': user.donated_gifts.count(),
        'items_received': user.received_gifts.count(),
        'active_requests': user.gift_requests.count(),
    }
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=user)
    
    return render(request, 'profile.html', {
        'form': form,
        'user_stats': user_stats
    })
    
    return render(request, 'profile.html', {'form': form})
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .models import User
from .forms import CustomUserCreationForm

from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to GiveNGet, {user.name}! Your account has been created successfully.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})
    
    return render(request, 'registration/register.html', {'form': form})
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def custom_logout(request):
    logout(request)
    return redirect('home')