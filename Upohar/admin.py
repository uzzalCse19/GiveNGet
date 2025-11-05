from django.contrib import admin
from django.utils.html import format_html
from .models import Category, UpoharPost, UpoharRequest

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'post_count', 'created']
    list_filter = ['is_active']
    search_fields = ['name']
    list_editable = ['is_active']
    actions = ['activate_categories', 'deactivate_categories']

    def post_count(self, obj):
        return obj.upoharpost_set.count()
    post_count.short_description = 'Total Posts'

    def created(self, obj):
        return obj.upoharpost_set.first().created_at if obj.upoharpost_set.exists() else 'No posts'
    created.short_description = 'First Post Date'

    def activate_categories(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} categories activated successfully.')
    activate_categories.short_description = "Activate selected categories"

    def deactivate_categories(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} categories deactivated successfully.')
    deactivate_categories.short_description = "Deactivate selected categories"

class UpoharRequestInline(admin.TabularInline):
    model = UpoharRequest
    extra = 0
    readonly_fields = ['requester', 'message', 'created_at']
    can_delete = False
    max_num = 0

    def has_add_permission(self, request, obj=None):
        return False

class UpoharPostAdmin(admin.ModelAdmin):
    list_display = [
        'title', 
        'donor', 
        'type', 
        'status', 
        'category', 
        'city', 
        'created_at', 
        'request_count',
        'image_preview'
    ]
    list_filter = ['type', 'status', 'category', 'created_at']
    search_fields = ['title', 'description', 'donor__name', 'donor__email', 'city']
    readonly_fields = ['created_at', 'updated_at', 'image_preview_large']
    list_editable = ['status']
    inlines = [UpoharRequestInline]
    actions = ['mark_as_available', 'mark_as_completed', 'mark_as_requested']

    fieldsets = (
        ('Basic Information', {
            'fields': ('donor', 'receiver', 'category', 'type', 'title', 'description')
        }),
        ('Location & Image', {
            'fields': ('city', 'image', 'image_preview_large')
        }),
        ('Exchange Details', {
            'fields': ('exchange_item_name', 'exchange_item_description'),
            'classes': ('collapse',)
        }),
        ('Status & Timestamps', {
            'fields': ('status', 'created_at', 'updated_at')
        }),
    )

    def request_count(self, obj):
        count = obj.requests.count()
        color = 'red' if count > 0 else 'gray'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            count
        )
    request_count.short_description = 'Requests'

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />',
                obj.image.url
            )
        return "No Image"
    image_preview.short_description = 'Image'

    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 200px; height: 200px; object-fit: cover;" />',
                obj.image.url
            )
        return "No Image Available"
    image_preview_large.short_description = 'Image Preview'

    def mark_as_available(self, request, queryset):
        updated = queryset.update(status='available')
        self.message_user(request, f'{updated} posts marked as available.')
    mark_as_available.short_description = "Mark selected posts as available"

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} posts marked as completed.')
    mark_as_completed.short_description = "Mark selected posts as completed"

    def mark_as_requested(self, request, queryset):
        updated = queryset.update(status='requested')
        self.message_user(request, f'{updated} posts marked as requested.')
    mark_as_requested.short_description = "Mark selected posts as requested"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('donor', 'receiver', 'category')

class UpoharRequestAdmin(admin.ModelAdmin):
    list_display = [
        'gift_title',
        'requester_info',
        'status',
        'donor_info',
        'created_at',
        'message_preview'
    ]
    list_filter = ['status', 'created_at']
    search_fields = [
        'gift__title', 
        'requester__name', 
        'requester__email',
        'gift__donor__name',
        'gift__donor__email'
    ]
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status']
    actions = ['approve_requests', 'reject_requests', 'mark_as_completed']

    fieldsets = (
        ('Request Information', {
            'fields': ('gift', 'requester', 'message', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def gift_title(self, obj):
        return format_html(
            '<strong>{}</strong><br><small>Type: {}</small>',
            obj.gift.title,
            obj.gift.get_type_display()
        )
    gift_title.short_description = 'Gift'

    def requester_info(self, obj):
        return format_html(
            '{}<br><small>{}</small><br><small>{}</small>',
            obj.requester.name,
            obj.requester.email,
            obj.requester.get_role_display()
        )
    requester_info.short_description = 'Requester'

    def donor_info(self, obj):
        return format_html(
            '{}<br><small>{}</small>',
            obj.gift.donor.name,
            obj.gift.donor.email
        )
    donor_info.short_description = 'Donor'

    def message_preview(self, obj):
        if obj.message:
            preview = obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
            return format_html(
                '<span title="{}">{}</span>',
                obj.message,
                preview
            )
        return "No message"
    message_preview.short_description = 'Message'

    def approve_requests(self, request, queryset):
        for req in queryset:
            if req.status == 'pending':
                # Approve this request and reject others for the same gift
                UpoharRequest.objects.filter(
                    gift=req.gift
                ).exclude(id=req.id).update(status='rejected')
                req.status = 'approved'
                req.gift.status = 'requested'
                req.gift.receiver = req.requester
                req.gift.save()
                req.save()
        self.message_user(request, f'{queryset.count()} requests approved.')
    approve_requests.short_description = "Approve selected requests"

    def reject_requests(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} requests rejected.')
    reject_requests.short_description = "Reject selected requests"

    def mark_as_completed(self, request, queryset):
        for req in queryset:
            req.status = 'completed'
            req.gift.status = 'completed'
            req.gift.save()
            req.save()
            
            # Update user stats
            req.gift.donor.completed_transactions += 1
            req.gift.donor.save()
            if req.requester.role in ['receiver', 'exchanger']:
                req.requester.completed_transactions += 1
                req.requester.save()
                
        self.message_user(request, f'{queryset.count()} requests marked as completed.')
    mark_as_completed.short_description = "Mark selected as completed"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'gift', 'gift__donor', 'requester'
        )

# Register models
admin.site.register(Category, CategoryAdmin)
admin.site.register(UpoharPost, UpoharPostAdmin)
admin.site.register(UpoharRequest, UpoharRequestAdmin)