from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]
    
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^(?:\+?88)?01[3-9]\d{8}$',
            message="Enter a valid Bangladeshi phone number"
        )]
    )
    # REMOVED: role field - no user roles
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    address = models.TextField(blank=True)
    total_donations = models.PositiveIntegerField(default=0)
    completed_donations = models.PositiveIntegerField(default=0)  # Changed from completed_transactions
    completed_exchanges = models.PositiveIntegerField(default=0)  # New field for exchanges
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        blank=True,
        help_text='The groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.name} ({self.email})"
    
    @property
    def badge_level(self):
        # Badge ONLY based on completed donations, NOT exchanges
        if self.completed_donations >= 50:
            return '🏅 Super Donor'
        elif self.completed_donations >= 20:
            return '🌟 Regular Donor'
        elif self.completed_donations >= 5:
            return '⭐ Beginner Donor'
        return '🆕 None'
    
    @property
    def total_completed_transactions(self):
        # Total of both donations and exchanges for statistics
        return self.completed_donations + self.completed_exchanges

from django.db import models
from django.utils import timezone
from datetime import timedelta
import secrets

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    def is_valid(self):
        # Token expires after 1 hour
        return not self.is_used and (timezone.now() - self.created_at) < timedelta(hours=1)
    
    def mark_as_used(self):
        self.is_used = True
        self.save()
    
    @classmethod
    def create_token(cls, user):
        # Delete any existing tokens for this user
        cls.objects.filter(user=user).delete()
        
        # Create new token
        token = secrets.token_urlsafe(50)
        return cls.objects.create(user=user, token=token)
    
    def __str__(self):
        return f"Reset token for {self.user.email}"