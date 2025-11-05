from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = [
        'email', 
        'name', 
        'role_display', 
        'status_display', 
        'is_staff', 
        'is_superuser',
        'completed_transactions',
        'badge_display',
        'profile_photo_preview',
        'date_joined'
    ]
    list_filter = [
        'role', 
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
        'badge_info'
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
        ('Role & Status', {
            'fields': (
                'role', 
                'status',
                'badge_info',
                'completed_transactions',
                'total_donations'
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
                'role',
                'is_staff', 
                'is_superuser'
            ),
        }),
    )

    def role_display(self, obj):
        colors = {
            'donor': 'green',
            'receiver': 'blue',
            'exchanger': 'orange'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.role, 'black'),
            obj.get_role_display()
        )
    role_display.short_description = 'Role'

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
            '<strong>{}</strong><br><small>Completed Transactions: {}</small>',
            obj.badge_level,
            obj.completed_transactions
        )
    badge_info.short_description = 'Badge Information'

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

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Make role field editable only for non-superusers when creating new users
        if obj is None and not request.user.is_superuser:
            form.base_fields['role'].disabled = True
        return form

# Register the custom User model with the custom admin interface
admin.site.register(User, CustomUserAdmin)

# Optional: Customize admin site header and title
admin.site.site_header = "Upohar Administration"
admin.site.site_title = "Upohar Admin Portal"
admin.site.index_title = "Welcome to Upohar Administration"