from django.shortcuts import render
from django.db import IntegrityError
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
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncMonth
from django.urls import reverse
# Template Views
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncMonth
from Upohar.models import User, UpoharPost, UpoharRequest, Category
# views.py - Add these views
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from .models import User
from .forms import CustomUserCreationForm

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from .forms import CustomUserCreationForm
from .models import User

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
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()  # This triggers the signal automatically
            
            messages.success(
                request, 
                'Registration successful! Please check your email to activate your account.'
            )
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

def send_manual_activation_email(user):
    """Send activation email manually"""
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_encode
    from django.utils.encoding import force_bytes
    from django.core.mail import send_mail
    from django.conf import settings
    
    print(f"🔧 Sending activation email to: {user.email}")
    
    # Generate token
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    # Test token immediately
    token_valid = default_token_generator.check_token(user, token)
    print(f"🔧 Token valid immediately: {token_valid}")
    
    activation_url = f"{settings.FRONTEND_URL}/activate/{uid}/{token}/"
    print(f"🔗 Activation URL: {activation_url}")
    
    subject = 'Activate Your Upohar Account'
    message = f'''
Hello {user.name},

Welcome to Upohar! Please activate your account by clicking the link below:

{activation_url}

This link will expire in 24 hours.

If you didn't create an account, please ignore this email.

Best regards,
Upohar Team
    '''
    
    try:
        send_mail(
            subject=subject,
            message=message.strip(),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        print(f"✅ Activation email sent successfully to {user.email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send activation email: {e}")
        return False
    

def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, "✅ Your account has been activated successfully! You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "❌ Activation link is invalid or has expired.")
            return redirect('register')

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, "❌ Activation link is invalid or has expired.")
        return redirect('register')


import json
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@require_http_methods(["POST"])
def resend_activation(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')

        if not email:
            return JsonResponse({'success': False, 'message': 'Email is required.'})

        try:
            user = User.objects.get(email=email)
            if user.is_active:
                return JsonResponse({'success': False, 'message': 'Account is already active.'})

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            activation_url = f"{settings.FRONTEND_URL}/activate/{uid}/{token}/"

            subject = "Activate Your Upohar Account"
            message = f"""
Hello {user.name},

You requested a new activation link. Please activate your account by clicking the link below:

{activation_url}

This link will expire in 24 hours.

If you didn't request this, please ignore this email.

Best regards,
Upohar Team
            """

            send_mail(
                subject=subject,
                message=message.strip(),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            return JsonResponse({'success': True, 'message': 'Activation email sent successfully.'})

        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'No account found with this email.'})

    except Exception as e:
        print(f"Error in resend_activation: {e}")
        return JsonResponse({'success': False, 'message': 'An error occurred.'})

def custom_login(request):
    if request.method == 'POST':
        email = request.POST.get('username')  # Django auth uses 'username' field
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                messages.error(
                    request, 
                    'Your account is not activated. Please check your email for the activation link.'
                )
                return render(request, 'registration/login.html')
        except User.DoesNotExist:
            pass
        
        # Authenticate user
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.name}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'registration/login.html')

@login_required
def dashboard(request):
    user = request.user
    context = {'user': user}
    
    # Check if user is admin/staff
    if user.is_active and (user.is_staff or user.is_superuser):
        return admin_dashboard(request)
    
    return user_dashboard(request)

def admin_dashboard(request):
    user = request.user
    if not (user.is_staff or user.is_superuser):
        return redirect('user_dashboard')
    
    # Get active section from URL parameter
    active_section = request.GET.get('section', 'overview')
    
    context = {
        'user': user,
        'active_section': active_section,
        'is_admin': True
    }
    
    # Load different data based on active section
    if active_section == 'overview':
        context.update(get_admin_overview_data())
    elif active_section == 'users':
        context.update(get_admin_users_data(request))
    elif active_section == 'posts':
        context.update(get_admin_posts_data(request))
    elif active_section == 'requests':
        context.update(get_admin_requests_data(request))
    elif active_section == 'categories':
        result = get_admin_categories_data(request)
    # redirect না হলে update
        if isinstance(result, dict):
            context.update(result)
        else:
            return result  # redirect হলে তা return করুন

    
    return render(request, 'admin_dashboard.html', context)
    
def user_dashboard(request):
    user = request.user
    
    # Get active section from URL parameter
    active_section = request.GET.get('section', 'overview')
    
    context = {
        'user': user,
        'active_section': active_section,
        'is_admin': False
    }
    
    # Load different data based on active section
    if active_section == 'overview':
        context.update(get_user_overview_data(user))
    elif active_section == 'my_posts':
        context.update(get_user_posts_data(user))
    elif active_section == 'my_requests':
        context.update(get_user_requests_data(user))
    elif active_section == 'received_requests':
        context.update(get_user_received_requests_data(user))
    
    return render(request, 'user_dashboard.html', context)

# Admin Data Functions
def get_admin_overview_data():
    total_users = User.objects.count()
    active_users = User.objects.filter(status='active').count()
    suspended_users = User.objects.filter(status='suspended').count()
    new_users_today = User.objects.filter(
        date_joined__date=timezone.now().date()
    ).count()
    
    total_posts = UpoharPost.objects.count()
    available_posts = UpoharPost.objects.filter(status='available').count()
    requested_posts = UpoharPost.objects.filter(status='requested').count()
    completed_posts = UpoharPost.objects.filter(status='completed').count()
    
    total_requests = UpoharRequest.objects.count()
    pending_requests = UpoharRequest.objects.filter(status='pending').count()
    approved_requests = UpoharRequest.objects.filter(status='approved').count()
    rejected_requests = UpoharRequest.objects.filter(status='rejected').count()
    completed_requests = UpoharRequest.objects.filter(status='completed').count()
    
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_posts = UpoharPost.objects.select_related('donor', 'category').order_by('-created_at')[:5]
    recent_requests = UpoharRequest.objects.select_related('gift', 'requester').order_by('-created_at')[:5]
    
    category_stats = Category.objects.annotate(
        post_count=Count('upoharpost'),
        available_posts=Count('upoharpost', filter=Q(upoharpost__status='available')),
        completed_posts=Count('upoharpost', filter=Q(upoharpost__status='completed'))
    ).order_by('-post_count')
    
    active_categories = Category.objects.filter(is_active=True).count()
    inactive_categories = Category.objects.filter(is_active=False).count()
    
    top_donors = User.objects.filter(
        completed_donations__gt=0
    ).order_by('-completed_donations')[:5]
    
    return {
        'total_users': total_users,
        'active_users': active_users,
        'suspended_users': suspended_users,
        'new_users_today': new_users_today,
        'total_posts': total_posts,
        'available_posts': available_posts,
        'requested_posts': requested_posts,
        'completed_posts': completed_posts,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'rejected_requests': rejected_requests,
        'completed_requests': completed_requests,
        'recent_users': recent_users,
        'recent_posts': recent_posts,
        'recent_requests': recent_requests,
        'category_stats': category_stats,
        'active_categories': active_categories,
        'inactive_categories': inactive_categories,
        'top_donors': top_donors,
    }

def get_admin_users_data(request):
    users = User.objects.all().order_by('-date_joined')
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        user = get_object_or_404(User, id=user_id)
        
        # Prevent suspending/deleting superuser/staff
        if user.is_superuser or user.is_staff:
            messages.error(request, "You cannot modify admin/staff users.")
            return redirect(f"{reverse('dashboard')}?section=users")
        
        if action == 'suspend':
            user.status = 'suspended'
            user.save()
            messages.success(request, f'User {user.name} has been suspended.')
        elif action == 'activate':
            user.status = 'active'
            user.save()
            messages.success(request, f'User {user.name} has been activated.')
        elif action == 'delete':
            if user != request.user:
                user.delete()
                messages.success(request, f'User {user.name} has been deleted.')
            else:
                messages.error(request, 'You cannot delete your own account.')
        
        return redirect(f"{reverse('dashboard')}?section=users")
    
    return {'users': users}

def get_admin_posts_data(request):
    posts = UpoharPost.objects.all().select_related('donor', 'category').order_by('-created_at')
    
    # Handle post actions
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        action = request.POST.get('action')
        post = get_object_or_404(UpoharPost, id=post_id)
        
        if action == 'delete':
            post.delete()
            messages.success(request, f'Post "{post.title}" has been deleted.')
        elif action == 'edit_status':
            new_status = request.POST.get('status')
            post.status = new_status
            post.save()
            messages.success(request, f'Post status updated to {new_status}.')
        
        return redirect('dashboard?section=posts')
    
    return {'all_posts': posts}

def get_admin_requests_data(request):
    requests = UpoharRequest.objects.all().select_related('gift', 'requester', 'gift__donor').order_by('-created_at')

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        requests = requests.filter(status=status_filter)

    # Count for each status (global, not filtered)
    pending_count = UpoharRequest.objects.filter(status='pending').count()
    approved_count = UpoharRequest.objects.filter(status='approved').count()
    rejected_count = UpoharRequest.objects.filter(status='rejected').count()
    completed_count = UpoharRequest.objects.filter(status='completed').count()

    # Handle actions
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        upohar_request = get_object_or_404(UpoharRequest, id=request_id)

        if action == 'approve':
            UpoharRequest.objects.filter(gift=upohar_request.gift).exclude(id=request_id).update(status='rejected')
            upohar_request.status = 'approved'
            upohar_request.gift.status = 'requested'
            upohar_request.gift.receiver = upohar_request.requester
            upohar_request.gift.save()
            upohar_request.save()
            messages.success(request, "Request has been approved.")

        elif action == 'reject':
            upohar_request.status = 'rejected'
            upohar_request.save()
            messages.success(request, "Request has been rejected.")

        elif action == 'complete':
            upohar_request.status = 'completed'
            upohar_request.gift.status = 'completed'
            upohar_request.gift.save()
            upohar_request.save()

            if upohar_request.gift.type == 'donation':
                upohar_request.gift.donor.completed_donations += 1
                upohar_request.gift.donor.save()
                upohar_request.requester.completed_donations += 1
                upohar_request.requester.save()
            else:
                upohar_request.gift.donor.completed_exchanges += 1
                upohar_request.gift.donor.save()
                upohar_request.requester.completed_exchanges += 1
                upohar_request.requester.save()

            messages.success(request, "Request marked as completed.")

        elif action == 'delete':
            upohar_request.delete()
            messages.success(request, "Request has been deleted.")

        return redirect('dashboard?section=requests' + (f'&status={status_filter}' if status_filter else ''))

    return {
        'all_requests': requests,
        'status_filter': status_filter,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'completed_count': completed_count,
    }



def get_admin_categories_data(request):
    # Get all categories with post count
    categories = Category.objects.all().annotate(
        post_count=Count('upoharpost')
    ).order_by('name')

    # Count active/inactive categories
    active_count = categories.filter(is_active=True).count()
    inactive_count = categories.filter(is_active=False).count()
    
    if request.method == 'POST':
        # Add new category
        if 'add_category' in request.POST:
            name = request.POST.get('name')
            if name:
                # Check for duplicates
                if Category.objects.filter(name__iexact=name).exists():
                    messages.error(request, f'Category "{name}" already exists.')
                else:
                    Category.objects.create(name=name)
                    messages.success(request, f'Category "{name}" has been added.')
        
        # Toggle category active status
        elif 'toggle_category' in request.POST:
            category_id = request.POST.get('category_id')
            category = get_object_or_404(Category, id=category_id)
            category.is_active = not category.is_active
            category.save()
            messages.success(
                request,
                f'Category "{category.name}" has been {"activated" if category.is_active else "deactivated"}.'
            )
        
        # Delete category
        elif 'delete_category' in request.POST:
            category_id = request.POST.get('category_id')
            category = get_object_or_404(Category, id=category_id)
            category_name = category.name
            category.delete()
            messages.success(request, f'Category "{category_name}" has been deleted.')
        
        # Redirect to the same section after POST
        return redirect(f"{reverse('dashboard')}?section=categories")
    
    # For GET request, return context dict
    return {
        'categories': categories,
        'active_count': active_count,
        'inactive_count': inactive_count,
    }


# User Data Functions
def get_user_overview_data(user):
    posts = UpoharPost.objects.filter(donor=user).order_by('-created_at')
    requests_received = UpoharRequest.objects.filter(gift__donor=user).order_by('-created_at')
    requests_sent = UpoharRequest.objects.filter(requester=user).order_by('-created_at')
    received_items = UpoharPost.objects.filter(receiver=user).order_by('-updated_at')
    
    total_posts = posts.count()
    donation_posts = posts.filter(type='donation').count()
    exchange_posts = posts.filter(type='exchange').count()
    available_posts = posts.filter(status='available').count()
    requested_posts = posts.filter(status='requested').count()
    completed_posts = posts.filter(status='completed').count()
    
    pending_requests_received = requests_received.filter(status='pending').count()
    approved_requests_received = requests_received.filter(status='approved').count()
    pending_requests_sent = requests_sent.filter(status='pending').count()
    approved_requests_sent = requests_sent.filter(status='approved').count()
    
    total_received = received_items.count()
    received_donations = received_items.filter(type='donation').count()
    received_exchanges = received_items.filter(type='exchange').count()
    
    total_users = User.objects.count()
    total_community_posts = UpoharPost.objects.count()
    total_community_requests = UpoharRequest.objects.count()
    active_categories = Category.objects.filter(is_active=True).count()
    
    return {
        'posts': posts[:5],
        'requests_received': requests_received[:5],
        'requests_sent': requests_sent[:5],
        'received_items': received_items[:5],
        'total_posts': total_posts,
        'donation_posts': donation_posts,
        'exchange_posts': exchange_posts,
        'available_posts': available_posts,
        'requested_posts': requested_posts,
        'completed_posts': completed_posts,
        'pending_requests_received': pending_requests_received,
        'approved_requests_received': approved_requests_received,
        'pending_requests_sent': pending_requests_sent,
        'approved_requests_sent': approved_requests_sent,
        'total_received': total_received,
        'received_donations': received_donations,
        'received_exchanges': received_exchanges,
        'total_users': total_users,
        'total_requests': total_community_requests,
        'active_categories': active_categories,
    }

def get_user_posts_data(user):
    posts = UpoharPost.objects.filter(donor=user).order_by('-created_at')
    return {'user_posts': posts}

def get_user_requests_data(user):
    requests_sent = UpoharRequest.objects.filter(requester=user).order_by('-created_at')
    return {'requests_sent': requests_sent}

def get_user_received_requests_data(user):
    requests_received = UpoharRequest.objects.filter(gift__donor=user).order_by('-created_at')
    return {'requests_received': requests_received}

# @login_required
# def dashboard(request):
#     user = request.user
#     context = {'user': user}
    
#     # Check if user is admin/staff
#     if user.is_active and (user.is_staff or user.is_superuser):
#         total_users = User.objects.count()
#         active_users = User.objects.filter(status='active').count()
#         suspended_users = User.objects.filter(status='suspended').count()
#         new_users_today = User.objects.filter(
#             date_joined__date=timezone.now().date()
#         ).count()
        
#         # Role Distribution
#         role_distribution = User.objects.values('role').annotate(
#             count=Count('id')
#         ).order_by('role')
        
#         # Post Statistics
#         total_posts = UpoharPost.objects.count()
#         available_posts = UpoharPost.objects.filter(status='available').count()
#         requested_posts = UpoharPost.objects.filter(status='requested').count()
#         completed_posts = UpoharPost.objects.filter(status='completed').count()
        
#         # Post Type Distribution
#         post_type_distribution = UpoharPost.objects.values('type').annotate(
#             count=Count('id')
#         ).order_by('type')
        
#         # Request Statistics
#         total_requests = UpoharRequest.objects.count()
#         pending_requests = UpoharRequest.objects.filter(status='pending').count()
#         approved_requests = UpoharRequest.objects.filter(status='approved').count()
#         rejected_requests = UpoharRequest.objects.filter(status='rejected').count()
#         completed_requests = UpoharRequest.objects.filter(status='completed').count()
        
#         # Recent Activity
#         recent_users = User.objects.order_by('-date_joined')[:5]
#         recent_posts = UpoharPost.objects.select_related('donor', 'category').order_by('-created_at')[:5]
#         recent_requests = UpoharRequest.objects.select_related('gift', 'requester').order_by('-created_at')[:5]
        
#         # Category Statistics
#         category_stats = Category.objects.annotate(
#             post_count=Count('upoharpost'),
#             available_posts=Count('upoharpost', filter=Q(upoharpost__status='available')),
#             completed_posts=Count('upoharpost', filter=Q(upoharpost__status='completed'))
#         ).order_by('-post_count')
        
#         # Monthly Growth Data (Last 6 months)
#         six_months_ago = timezone.now() - timedelta(days=180)
        
#         # User growth by month
#         user_growth = (
#         User.objects.filter(date_joined__gte=six_months_ago)
#         .annotate(month=TruncMonth('date_joined'))
#         .values('month')
#        .annotate(count=Count('id'))
#        .order_by('month')
#        )
        
#         # Post growth by month
#         post_growth = (
#         UpoharPost.objects.filter(created_at__gte=six_months_ago)
#         .annotate(month=TruncMonth('created_at'))
#        .values('month')
#        .annotate(count=Count('id'))
#        .order_by('month')
#       )
        
#         # Top Donors
#         top_donors = User.objects.filter(
#             completed_transactions__gt=0
#         ).order_by('-completed_transactions')[:5]
        
#         # System Health
#         inactive_categories = Category.objects.filter(is_active=False).count()
#         posts_without_images = UpoharPost.objects.filter(image__isnull=True).count()
        
#         context.update({
#             # User Stats
#             'total_users': total_users,
#             'active_users': active_users,
#             'suspended_users': suspended_users,
#             'new_users_today': new_users_today,
#             'role_distribution': list(role_distribution),
            
#             # Post Stats
#             'total_posts': total_posts,
#             'available_posts': available_posts,
#             'requested_posts': requested_posts,
#             'completed_posts': completed_posts,
#             'post_type_distribution': list(post_type_distribution),
            
#             # Request Stats
#             'total_requests': total_requests,
#             'pending_requests': pending_requests,
#             'approved_requests': approved_requests,
#             'rejected_requests': rejected_requests,
#             'completed_requests': completed_requests,
            
#             # Recent Activity
#             'recent_users': recent_users,
#             'recent_posts': recent_posts,
#             'recent_requests': recent_requests,
            
#             # Category Stats
#             'category_stats': category_stats,
#             'inactive_categories': inactive_categories,
#             'posts_without_images': posts_without_images,
            
#             # Growth Data
#             'user_growth': list(user_growth),
#             'post_growth': list(post_growth),
            
#             # Top Performers
#             'top_donors': top_donors,
            
#             # Chart Data (for JavaScript)
#             'chart_data': {
#                 'roles': [item['role'] for item in role_distribution],
#                 'role_counts': [item['count'] for item in role_distribution],
#                 'post_types': [item['type'] for item in post_type_distribution],
#                 'post_type_counts': [item['count'] for item in post_type_distribution],
#                 'request_statuses': ['Pending', 'Approved', 'Rejected', 'Completed'],
#                 'request_counts': [pending_requests, approved_requests, rejected_requests, completed_requests],
#             }
#         })
#         return render(request, 'admin_dashboard.html', context)
    
#     # Single dashboard for all regular users
#     posts = UpoharPost.objects.filter(donor=user).order_by('-created_at')
#     requests_received = UpoharRequest.objects.filter(gift__donor=user).order_by('-created_at')
#     requests_sent = UpoharRequest.objects.filter(requester=user).order_by('-created_at')
#     received_items = UpoharPost.objects.filter(receiver=user).order_by('-updated_at')
    
#     # Statistics
#     total_posts = posts.count()
#     donation_posts = posts.filter(type='donation').count()
#     exchange_posts = posts.filter(type='exchange').count()
#     available_posts = posts.filter(status='available').count()
#     requested_posts = posts.filter(status='requested').count()
#     completed_posts = posts.filter(status='completed').count()
    
#     pending_requests_received = requests_received.filter(status='pending').count()
#     approved_requests_received = requests_received.filter(status='approved').count()
#     pending_requests_sent = requests_sent.filter(status='pending').count()
#     approved_requests_sent = requests_sent.filter(status='approved').count()
    
#     total_received = received_items.count()
#     received_donations = received_items.filter(type='donation').count()
#     received_exchanges = received_items.filter(type='exchange').count()
    
#     context.update({
#         'posts': posts[:5],
#         'requests_received': requests_received[:5],
#         'requests_sent': requests_sent[:5],
#         'received_items': received_items[:5],
#         'total_posts': total_posts,
#         'donation_posts': donation_posts,
#         'exchange_posts': exchange_posts,
#         'available_posts': available_posts,
#         'requested_posts': requested_posts,
#         'completed_posts': completed_posts,
#         'pending_requests_received': pending_requests_received,
#         'approved_requests_received': approved_requests_received,
#         'pending_requests_sent': pending_requests_sent,
#         'approved_requests_sent': approved_requests_sent,
#         'total_received': total_received,
#         'received_donations': received_donations,
#         'received_exchanges': received_exchanges,
#     })
    
#     return render(request, 'user_dashboard.html', context)

@login_required
def manage_requests(request):
    user = request.user
    
    # All users can manage requests for their posts and see their sent requests
    received_requests = UpoharRequest.objects.filter(gift__donor=user).order_by('-created_at')
    sent_requests = UpoharRequest.objects.filter(requester=user).order_by('-created_at')
    
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        
        upohar_request = get_object_or_404(UpoharRequest, id=request_id, gift__donor=user)
        
        if action == 'approve':
            # Approve this request and reject others
            UpoharRequest.objects.filter(gift=upohar_request.gift).exclude(id=request_id).update(status='rejected')
            upohar_request.status = 'approved'
            upohar_request.gift.status = 'requested'
            upohar_request.gift.receiver = upohar_request.requester
            upohar_request.gift.save()
            upohar_request.save()
            
            messages.success(request, 'Request approved successfully!')
            
        elif action == 'reject':
            upohar_request.status = 'rejected'
            upohar_request.save()
            messages.success(request, 'Request rejected.')
        
        elif action == 'complete':
            upohar_request.status = 'completed'
            upohar_request.gift.status = 'completed'
            upohar_request.gift.save()
            upohar_request.save()
            
            # Update user stats based on post type
            if upohar_request.gift.type == 'donation':
                # Only update donation count for badges
                user.completed_donations += 1
                user.save()
                upohar_request.requester.completed_donations += 1
                upohar_request.requester.save()
            else:  # exchange
                # Update exchange count (no badge effect)
                user.completed_exchanges += 1
                user.save()
                upohar_request.requester.completed_exchanges += 1
                upohar_request.requester.save()
            
            messages.success(request, 'Transaction marked as completed!')
    
    return render(request, 'manage_requests.html', {
        'received_requests': received_requests,
        'sent_requests': sent_requests
    })


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
from django.contrib.auth import logout
@login_required
def custom_logout(request):
    logout(request)
    return redirect('home')



# def dashboard(request):
#     user = request.user
#     context = {'user': user}
    
#     # Check if user is admin/staff and redirect to admin dashboard
#     if user.is_active and (user.is_staff or user.is_superuser):
#         # User Statistics
#         total_users = User.objects.count()
#         active_users = User.objects.filter(status='active').count()
#         suspended_users = User.objects.filter(status='suspended').count()
#         new_users_today = User.objects.filter(
#             date_joined__date=timezone.now().date()
#         ).count()
        
#         # Role Distribution
#         role_distribution = User.objects.values('role').annotate(
#             count=Count('id')
#         ).order_by('role')
        
#         # Post Statistics
#         total_posts = UpoharPost.objects.count()
#         available_posts = UpoharPost.objects.filter(status='available').count()
#         requested_posts = UpoharPost.objects.filter(status='requested').count()
#         completed_posts = UpoharPost.objects.filter(status='completed').count()
        
#         # Post Type Distribution
#         post_type_distribution = UpoharPost.objects.values('type').annotate(
#             count=Count('id')
#         ).order_by('type')
        
#         # Request Statistics
#         total_requests = UpoharRequest.objects.count()
#         pending_requests = UpoharRequest.objects.filter(status='pending').count()
#         approved_requests = UpoharRequest.objects.filter(status='approved').count()
#         rejected_requests = UpoharRequest.objects.filter(status='rejected').count()
#         completed_requests = UpoharRequest.objects.filter(status='completed').count()
        
#         # Recent Activity
#         recent_users = User.objects.order_by('-date_joined')[:5]
#         recent_posts = UpoharPost.objects.select_related('donor', 'category').order_by('-created_at')[:5]
#         recent_requests = UpoharRequest.objects.select_related('gift', 'requester').order_by('-created_at')[:5]
        
#         # Category Statistics
#         category_stats = Category.objects.annotate(
#             post_count=Count('upoharpost'),
#             available_posts=Count('upoharpost', filter=Q(upoharpost__status='available')),
#             completed_posts=Count('upoharpost', filter=Q(upoharpost__status='completed'))
#         ).order_by('-post_count')
        
#         # Monthly Growth Data (Last 6 months)
#         six_months_ago = timezone.now() - timedelta(days=180)
        
#         # User growth by month
#         user_growth = (
#         User.objects.filter(date_joined__gte=six_months_ago)
#         .annotate(month=TruncMonth('date_joined'))
#         .values('month')
#        .annotate(count=Count('id'))
#        .order_by('month')
#        )
        
#         # Post growth by month
#         post_growth = (
#         UpoharPost.objects.filter(created_at__gte=six_months_ago)
#         .annotate(month=TruncMonth('created_at'))
#        .values('month')
#        .annotate(count=Count('id'))
#        .order_by('month')
#       )
        
#         # Top Donors
#         top_donors = User.objects.filter(
#             completed_transactions__gt=0
#         ).order_by('-completed_transactions')[:5]
        
#         # System Health
#         inactive_categories = Category.objects.filter(is_active=False).count()
#         posts_without_images = UpoharPost.objects.filter(image__isnull=True).count()
        
#         context.update({
#             # User Stats
#             'total_users': total_users,
#             'active_users': active_users,
#             'suspended_users': suspended_users,
#             'new_users_today': new_users_today,
#             'role_distribution': list(role_distribution),
            
#             # Post Stats
#             'total_posts': total_posts,
#             'available_posts': available_posts,
#             'requested_posts': requested_posts,
#             'completed_posts': completed_posts,
#             'post_type_distribution': list(post_type_distribution),
            
#             # Request Stats
#             'total_requests': total_requests,
#             'pending_requests': pending_requests,
#             'approved_requests': approved_requests,
#             'rejected_requests': rejected_requests,
#             'completed_requests': completed_requests,
            
#             # Recent Activity
#             'recent_users': recent_users,
#             'recent_posts': recent_posts,
#             'recent_requests': recent_requests,
            
#             # Category Stats
#             'category_stats': category_stats,
#             'inactive_categories': inactive_categories,
#             'posts_without_images': posts_without_images,
            
#             # Growth Data
#             'user_growth': list(user_growth),
#             'post_growth': list(post_growth),
            
#             # Top Performers
#             'top_donors': top_donors,
            
#             # Chart Data (for JavaScript)
#             'chart_data': {
#                 'roles': [item['role'] for item in role_distribution],
#                 'role_counts': [item['count'] for item in role_distribution],
#                 'post_types': [item['type'] for item in post_type_distribution],
#                 'post_type_counts': [item['count'] for item in post_type_distribution],
#                 'request_statuses': ['Pending', 'Approved', 'Rejected', 'Completed'],
#                 'request_counts': [pending_requests, approved_requests, rejected_requests, completed_requests],
#             }
#         })
        
#         return render(request, 'admin_dashboard.html', context)
    
#     # Original dashboard logic for regular users
#     if user.role == 'donor' or user.is_donor_user:
#         posts = UpoharPost.objects.filter(donor=user).order_by('-created_at')
#         requests = UpoharRequest.objects.filter(gift__donor=user).order_by('-created_at')
        
#         # Statistics
#         total_posts = posts.count()
#         available_posts = posts.filter(status='available').count()
#         requested_posts = posts.filter(status='requested').count()
#         completed_posts = posts.filter(status='completed').count()
#         pending_requests = requests.filter(status='pending').count()
#         approved_requests = requests.filter(status='approved').count()
        
#         context.update({
#             'posts': posts[:5],  # Show only recent 5 posts
#             'requests': requests[:5],  # Show only recent 5 requests
#             'total_posts': total_posts,
#             'available_posts': available_posts,
#             'requested_posts': requested_posts,
#             'completed_posts': completed_posts,
#             'pending_requests': pending_requests,
#             'approved_requests': approved_requests,
#         })
#         template = 'donor_dashboard.html'
        
#     elif user.role == 'receiver':
#         received_gifts = UpoharPost.objects.filter(receiver=user).order_by('-updated_at')
#         requests = UpoharRequest.objects.filter(requester=user).order_by('-created_at')
        
#         # Statistics
#         total_received = received_gifts.count()
#         pending_requests = requests.filter(status='pending').count()
#         approved_requests = requests.filter(status='approved').count()
#         rejected_requests = requests.filter(status='rejected').count()
        
#         context.update({
#             'received_gifts': received_gifts[:5],
#             'requests': requests[:5],
#             'total_received': total_received,
#             'pending_requests': pending_requests,
#             'approved_requests': approved_requests,
#             'rejected_requests': rejected_requests,
#         })
#         template = 'receiver_dashboard.html'
        
#     elif user.role == 'exchanger':
#         posts = UpoharPost.objects.filter(donor=user).order_by('-created_at')
#         requests_sent = UpoharRequest.objects.filter(requester=user).order_by('-created_at')
#         requests_received = UpoharRequest.objects.filter(gift__donor=user).order_by('-created_at')
        
#         # Statistics
#         total_posts = posts.count()
#         available_posts = posts.filter(status='available').count()
#         sent_requests = requests_sent.count()
#         pending_sent = requests_sent.filter(status='pending').count()
#         received_requests = requests_received.count()
#         pending_received = requests_received.filter(status='pending').count()
        
#         context.update({
#             'posts': posts[:5],
#             'requests_sent': requests_sent[:5],
#             'requests_received': requests_received[:5],
#             'total_posts': total_posts,
#             'available_posts': available_posts,
#             'sent_requests': sent_requests,
#             'pending_sent': pending_sent,
#             'received_requests': received_requests,
#             'pending_received': pending_received,
#         })
#         template = 'exchanger_dashboard.html'
    
#     return render(request, template, context)
