from django.shortcuts import render
from Upohar.models import UpoharPost, Category
from django.contrib.auth.decorators import login_required
from .models import UpoharPost, Category
from .forms import UpoharPostForm
from Upohar.models import UpoharRequest
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
# Create your views here.
from django.db.models import Sum
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import UpoharPost, User, Category
from django.db.models import Q

from django.db.models import Count, Q

from django.db.models import Sum
from django.contrib.auth.decorators import login_required

# @login_required
def home(request):
    # Recent donation & exchange posts (select related to reduce queries)
    donation_posts = (
        UpoharPost.objects.filter(type='donation', status='available')
        .select_related('category', 'donor')
        .order_by('-created_at')[:6]
    )
    exchange_posts = (
        UpoharPost.objects.filter(type='exchange', status='available')
        .select_related('category', 'donor')
        .order_by('-created_at')[:6]
    )

    # Top donors
    top_donors = (
        User.objects.filter(completed_donations__gt=0)
        .only('name', 'profile_photo', 'completed_donations')
        .order_by('-completed_donations')[:4]
    )

    # Statistics - aggregate in a single query per model where possible
    user_stats = User.objects.aggregate(
        total_users=Sum(1),
        completed_donations=Sum('completed_donations'),
        completed_exchanges=Sum('completed_exchanges'),
    )

    total_posts = UpoharPost.objects.count()
    active_categories = Category.objects.filter(is_active=True).count()

    context = {
        'donation_posts': donation_posts,
        'exchange_posts': exchange_posts,
        'top_donors': top_donors,
        'total_users': user_stats['total_users'] or 0,
        'total_posts': total_posts,
        'completed_donations': user_stats['completed_donations'] or 0,
        'completed_exchanges': user_stats['completed_exchanges'] or 0,
        'active_categories': active_categories,
    }

    return render(request, 'home.html', context)

from django.db.models import Q
from django.contrib.auth.decorators import login_required

# @login_required
def post_list(request):
    # Prefetch and select related objects to avoid N+1 queries
    posts = (
        UpoharPost.objects
        .filter(status='available')
        .select_related('category', 'donor', 'receiver')  # foreign keys (1-to-1 or many-to-one)
        .order_by('-created_at')
    )

    # Get filters
    category_id = request.GET.get('category')
    post_type = request.GET.get('type')
    search_query = request.GET.get('search')

    # Apply filters efficiently
    if category_id:
        posts = posts.filter(category_id=category_id)
    if post_type:
        posts = posts.filter(type=post_type)
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(exchange_item_name__icontains=search_query)
            | Q(category__name__icontains=search_query)
            | Q(city__icontains=search_query)
        )

    # Categories (cacheable and small)
    categories = Category.objects.filter(is_active=True).only('id', 'name')

    return render(request, 'post_list.html', {
        'posts': posts,
        'categories': categories,
    })


@login_required
def create_post(request):
    user = request.user

    # Check permission - ALL authenticated users can create posts
    if not user.is_authenticated:
        messages.error(request, "You need to be logged in to create posts.")
        return redirect('login')

    if request.method == 'POST':
        form = UpoharPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.donor = user
            post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('home')
    else:
        form = UpoharPostForm()

    return render(request, 'create_post.html', {'form': form})


@login_required
def post_detail(request, pk):
    post = get_object_or_404(UpoharPost, pk=pk)
    user_has_requested = UpoharRequest.objects.filter(gift=post, requester=request.user).exists()
    
    return render(request, 'post_detail.html', {
        'post': post,
        'user_has_requested': user_has_requested,
    })

@login_required
def request_post(request, pk):
    post = get_object_or_404(UpoharPost, pk=pk)
    
    # Check if user can request this post
    if post.donor == request.user:
        messages.error(request, "You cannot request your own post.")
        return redirect('post_detail', pk=pk)
    
    if post.status != 'available':
        messages.error(request, "This post is no longer available.")
        return redirect('post_detail', pk=pk)
    
    # Check if user already requested
    if UpoharRequest.objects.filter(gift=post, requester=request.user).exists():
        messages.warning(request, "You have already requested this post.")
        return redirect('post_detail', pk=pk)
    
    if request.method == 'POST':
        message = request.POST.get('message', '')
        
        # Create request
        upohar_request = UpoharRequest.objects.create(
            gift=post,
            requester=request.user,
            message=message
        )
        
        # Send email to post creator
        try:
            send_mail(
                subject=f'New Request for Your Post: {post.title}',
                message=f'''
Hello {post.donor.name},

You have received a new request for your post "{post.title}".

Requester: {request.user.name} ({request.user.email})
Message: {message}

Please login to your dashboard to review this request.

Best regards,
Upohar Team
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[post.donor.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Email sending failed: {e}")
        
        messages.success(request, 'Request sent successfully!')
        return redirect('post_detail', pk=pk)
    
    return render(request, 'request_post.html', {'post': post})
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.contrib import messages
from django.db.models import Prefetch
from django.conf import settings

@login_required
def manage_requests(request):
    user = request.user

    # Use exists() (efficient single query)
    user_has_posts = UpoharPost.objects.filter(donor=user).exists()

    if user_has_posts:
        # Prefetch related objects for efficiency
        received_requests = (
            UpoharRequest.objects
            .filter(gift__donor=user)
            .select_related('gift__donor', 'gift__receiver', 'gift__category', 'requester')
            .order_by('-created_at')
        )

        if request.method == 'POST':
            request_id = request.POST.get('request_id')
            action = request.POST.get('action')

            upohar_request = get_object_or_404(
                UpoharRequest.objects.select_related('gift', 'requester', 'gift__donor'),
                id=request_id, gift__donor=user
            )

            if action == 'approve':
                # Bulk update to reject others efficiently
                UpoharRequest.objects.filter(gift=upohar_request.gift).exclude(id=request_id).update(status='rejected')
                
                upohar_request.status = 'approved'
                gift = upohar_request.gift
                gift.status = 'requested'
                gift.receiver = upohar_request.requester
                gift.save(update_fields=['status', 'receiver'])
                upohar_request.save(update_fields=['status'])

                # Send approval email
                try:
                    send_mail(
                        subject=f'Your Request Has Been Approved: {gift.title}',
                        message=f'''
Hello {upohar_request.requester.name},

Your request for "{gift.title}" has been approved!

Please contact the donor to arrange pickup/delivery.

Donor: {user.name} ({user.email})

Item Details:
- Title: {gift.title}
- Type: {gift.get_type_display()}
- Description: {gift.description}

Best regards,
Upohar Team
                        ''',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[upohar_request.requester.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f"Email sending failed: {e}")

                messages.success(request, 'Request approved successfully!')

            elif action == 'reject':
                upohar_request.status = 'rejected'
                upohar_request.save(update_fields=['status'])
                messages.success(request, 'Request rejected.')

            elif action == 'complete':
                upohar_request.status = 'completed'
                gift = upohar_request.gift
                gift.status = 'completed'
                gift.save(update_fields=['status'])
                upohar_request.save(update_fields=['status'])

                # Update stats efficiently
                if gift.type == 'donation':
                    User.objects.filter(pk__in=[user.pk, upohar_request.requester.pk]).update(
                        completed_donations=models.F('completed_donations') + 1
                    )
                else:
                    User.objects.filter(pk__in=[user.pk, upohar_request.requester.pk]).update(
                        completed_exchanges=models.F('completed_exchanges') + 1
                    )

                messages.success(request, 'Transaction marked as completed!')

            return redirect('manage_requests')

        # Sent requests (prefetch for user’s own requests)
        sent_requests = (
            UpoharRequest.objects
            .filter(requester=user)
            .select_related('gift__donor', 'gift__category')
            .order_by('-created_at')
        )

        return render(request, 'manage_requests.html', {
            'received_requests': received_requests,
            'sent_requests': sent_requests,
            'user_has_posts': user_has_posts,
        })

    else:
        # Requester only — no posts
        sent_requests = (
            UpoharRequest.objects
            .filter(requester=user)
            .select_related('gift__donor', 'gift__category')
            .order_by('-created_at')
        )

        return render(request, 'manage_requests.html', {
            'sent_requests': sent_requests,
            'received_requests': UpoharRequest.objects.none(),
            'user_has_posts': user_has_posts,
        })

# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UpoharPost
from .forms import UpoharPostForm

@login_required
def edit_post(request, pk):
    post = get_object_or_404(UpoharPost, pk=pk, donor=request.user)

    if request.method == 'POST':
        form = UpoharPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully!")
            return redirect('post_detail', pk=post.pk)
  # Replace with your actual post list view name
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UpoharPostForm(instance=post)

    return render(request, 'edit_post.html', {'form': form, 'post': post})

# @login_required
# def manage_requests(request):
#     user = request.user
    
#     if user.role == 'donor' or user.is_donor_user or user.role == 'exchanger':
#         # Requests for user's posts
#         received_requests = UpoharRequest.objects.filter(gift__donor=user).order_by('-created_at')
        
#         if request.method == 'POST':
#             request_id = request.POST.get('request_id')
#             action = request.POST.get('action')
            
#             upohar_request = get_object_or_404(UpoharRequest, id=request_id, gift__donor=user)
            
#             if action == 'approve':
#                 # Approve this request and reject others
#                 UpoharRequest.objects.filter(gift=upohar_request.gift).exclude(id=request_id).update(status='rejected')
#                 upohar_request.status = 'approved'
#                 upohar_request.gift.status = 'requested'
#                 upohar_request.gift.receiver = upohar_request.requester
#                 upohar_request.gift.save()
#                 upohar_request.save()
                
#                 # Send approval email
#                 try:
#                     send_mail(
#                         subject=f'Your Request Has Been Approved: {upohar_request.gift.title}',
#                         message=f'''
# Hello {upohar_request.requester.name},

# Your request for "{upohar_request.gift.title}" has been approved!

# Please contact the donor to arrange pickup/delivery.

# Donor: {user.name} ({user.email})
#      {item_details}

# Best regards,
# Upohar Team
#                         ''',
#                         from_email=settings.DEFAULT_FROM_EMAIL,
#                         recipient_list=[upohar_request.requester.email],
#                         fail_silently=False,
#                     )
#                 except Exception as e:
#                     print(f"Email sending failed: {e}")
                
#                 messages.success(request, 'Request approved successfully!')
                
#             elif action == 'reject':
#                 upohar_request.status = 'rejected'
#                 upohar_request.save()
#                 messages.success(request, 'Request rejected.')
            
#             elif action == 'complete':
#                 upohar_request.status = 'completed'
#                 upohar_request.gift.status = 'completed'
#                 upohar_request.gift.save()
#                 upohar_request.save()
                
#                 # Update user stats
#                 user.completed_transactions += 1
#                 user.save()
#                 if upohar_request.requester.role in ['receiver', 'exchanger']:
#                     upohar_request.requester.completed_transactions += 1
#                     upohar_request.requester.save()
                
#                 messages.success(request, 'Transaction marked as completed!')
        
#         return render(request, 'manage_requests.html', {'received_requests': received_requests})
    
#     else:
#         # For receivers - show their sent requests
#         sent_requests = UpoharRequest.objects.filter(requester=user).order_by('-created_at')
#         return render(request, 'manage_requests.html', {'sent_requests': sent_requests})
