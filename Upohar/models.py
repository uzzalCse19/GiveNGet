from django.db import models
from users.models import User
from django.utils import timezone
# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class UpoharPost(models.Model):
    TYPE_CHOICES = [
        ('donation', 'Donation'),
        ('exchange', 'Exchange'),  # Keep exchange type
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('requested', 'Requested'),
        ('completed', 'Completed'),
    ]
    
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donated_gifts')
    receiver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_gifts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='donation')  # Keep type field
    title = models.CharField(max_length=200)
    description = models.TextField()
    city = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='gifts/', null=True, blank=True)

    # Exchange-specific fields - keep them
    exchange_item_name = models.CharField(max_length=200, blank=True, null=True)
    exchange_item_description = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.get_type_display()} - {self.get_status_display()})"
    
class UpoharRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]

    gift = models.ForeignKey(UpoharPost, on_delete=models.CASCADE, related_name='requests')
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gift_requests')
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.requester.email} → {self.gift.title} ({self.status})"

    class Meta:
        unique_together = ('gift', 'requester')
        ordering = ['-created_at']

# class UpoharPost(models.Model):
#     TYPE_CHOICES = [
#         ('donation', 'Donation'),
#         ('exchange', 'Exchange'),
#     ]

#     STATUS_CHOICES = [
#         ('available', 'Available'),
#         ('requested', 'Requested'),
#         ('completed', 'Completed'),
#     ]
    
#     donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donated_gifts')
#     receiver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_gifts')
#     category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
#     type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='donation')
#     title = models.CharField(max_length=200)
#     description = models.TextField()
#     city = models.CharField(max_length=100, blank=True)
#     image = models.ImageField(upload_to='gifts/', null=True, blank=True)

#     # Exchange-specific fields
#     exchange_item_name = models.CharField(max_length=200, blank=True, null=True)
#     exchange_item_description = models.TextField(blank=True, null=True)

#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
#     created_at = models.DateTimeField(default=timezone.now)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.title} ({self.get_type_display()} - {self.get_status_display()})"
