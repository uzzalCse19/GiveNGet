from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = [
        'email', 
        'name', 
        'status_display', 
        'is_staff', 
        'is_superuser',
        'completed_donations',
        'completed_exchanges',
        'badge_display',
        'profile_photo_preview',
        'date_joined'
    ]
    list_filter = [
        'status', 
        'is_staff', 
        'is_superuser', 
        'date_joined'
    ]
    search_fields = ['email', 'name', 'phone']
    readonly_fields = [
        'date_joined', 
        'last_login', 
        'profile_photo_large',
        'badge_info',
        'total_completed_transactions'
    ]
    ordering = ['-date_joined']
    actions = [
        'activate_users', 
        'deactivate_users', 
        'suspend_users',
        'make_staff',
        'remove_staff'
    ]

    fieldsets = (
        ('Personal Info', {
            'fields': (
                'profile_photo', 
                'profile_photo_large',
                'name', 
                'email', 
                'phone', 
                'address'
            )
        }),
        ('Statistics', {
            'fields': (
                'completed_donations',
                'completed_exchanges',
                'total_completed_transactions',
                'badge_info',
            )
        }),
        ('Status', {
            'fields': (
                'status',
            )
        }),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff', 
                'is_superuser',
                'groups', 
                'user_permissions'
            )
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 
                'name', 
                'password1', 
                'password2', 
                'is_staff', 
                'is_superuser'
            ),
        }),
    )

    def status_display(self, obj):
        colors = {
            'active': 'green',
            'inactive': 'gray',
            'suspended': 'red'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_display.short_description = 'Status'

    def badge_display(self, obj):
        badges = {
            '🏅 Super Donor': 'gold',
            '🌟 Regular Donor': 'silver',
            '⭐ Beginner Donor': 'bronze',
            '🆕 Newbie': 'gray'
        }
        badge = obj.badge_level
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            badges.get(badge, 'black'),
            badge
        )
    badge_display.short_description = 'Badge'

    def profile_photo_preview(self, obj):
        if obj.profile_photo:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 50%;" />',
                obj.profile_photo.url
            )
        return format_html(
            '<div style="width: 40px; height: 40px; background: #f8f9fa; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #6c757d; font-size: 12px;">No Photo</div>'
        )
    profile_photo_preview.short_description = 'Photo'

    def profile_photo_large(self, obj):
        if obj.profile_photo:
            return format_html(
                '<img src="{}" style="width: 150px; height: 150px; object-fit: cover; border-radius: 8px;" />',
                obj.profile_photo.url
            )
        return "No Profile Photo"
    profile_photo_large.short_description = 'Profile Photo Preview'

    def badge_info(self, obj):
        return format_html(
            '<strong>{}</strong><br>'
            '<small>Completed Donations: {}</small><br>'
            '<small>Completed Exchanges: {}</small><br>'
            '<small>Total Transactions: {}</small>',
            obj.badge_level,
            obj.completed_donations,
            obj.completed_exchanges,
            obj.total_completed_transactions
        )
    badge_info.short_description = 'User Statistics'

    def total_completed_transactions(self, obj):
        return obj.completed_donations + obj.completed_exchanges
    total_completed_transactions.short_description = 'Total Transactions'

    def activate_users(self, request, queryset):
        updated = queryset.update(status='active', is_active=True)
        self.message_user(request, f'{updated} users activated successfully.')
    activate_users.short_description = "Activate selected users"

    def deactivate_users(self, request, queryset):
        updated = queryset.update(status='inactive', is_active=False)
        self.message_user(request, f'{updated} users deactivated.')
    deactivate_users.short_description = "Deactivate selected users"

    def suspend_users(self, request, queryset):
        updated = queryset.update(status='suspended', is_active=False)
        self.message_user(request, f'{updated} users suspended.')
    suspend_users.short_description = "Suspend selected users"

    def make_staff(self, request, queryset):
        updated = queryset.update(is_staff=True)
        self.message_user(request, f'{updated} users granted staff status.')
    make_staff.short_description = "Grant staff status to selected users"

    def remove_staff(self, request, queryset):
        # Don't allow removing staff status from superusers
        non_superusers = queryset.filter(is_superuser=False)
        updated = non_superusers.update(is_staff=False)
        self.message_user(request, f'{updated} users removed from staff (superusers excluded).')
    remove_staff.short_description = "Remove staff status from selected users"

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('groups', 'user_permissions')
    
from django.contrib import admin
from django.utils import timezone
from datetime import timedelta
from .models import PasswordResetToken

class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token_short', 'created_at', 'is_used', 'is_valid_display', 'expires_in']
    list_filter = ['is_used', 'created_at']
    search_fields = ['user__email', 'user__name', 'token']
    readonly_fields = ['token', 'created_at', 'is_valid_display', 'expires_in']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Token Information', {
            'fields': ('user', 'token', 'created_at')
        }),
        ('Status', {
            'fields': ('is_used', 'is_valid_display', 'expires_in')
        }),
    )
    
    def token_short(self, obj):
        """Display shortened version of token"""
        return f"{obj.token[:20]}..." if len(obj.token) > 20 else obj.token
    token_short.short_description = 'Token'
    
    def is_valid_display(self, obj):
        """Display whether token is valid"""
        return obj.is_valid()
    is_valid_display.boolean = True
    is_valid_display.short_description = 'Is Valid'
    
    def expires_in(self, obj):
        """Display time until expiration"""
        if obj.is_used:
            return "Used"
        
        expiration_time = obj.created_at + timedelta(hours=1)
        time_left = expiration_time - timezone.now()
        
        if time_left.total_seconds() <= 0:
            return "Expired"
        
        hours, remainder = divmod(int(time_left.total_seconds()), 3600)
        minutes = remainder // 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
    expires_in.short_description = 'Expires In'
    
    def get_queryset(self, request):
        """Optimize queryset with user data"""
        return super().get_queryset(request).select_related('user')
    
    def has_add_permission(self, request):
        """Prevent manual addition of tokens"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Allow only marking as used"""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion of tokens"""
        return True

# Register the model
admin.site.register(PasswordResetToken, PasswordResetTokenAdmin)

# Register the custom User model with the custom admin interface
admin.site.register(User, CustomUserAdmin)

# Optional: Customize admin site header and title
admin.site.site_header = "Upohar Administration"
admin.site.site_title = "Upohar Admin Portal"
admin.site.index_title = "Welcome to Upohar Administration"