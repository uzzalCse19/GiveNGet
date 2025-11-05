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
    ROLE_CHOICES = [
        ('donor', 'Donor'),
        ('receiver', 'Receiver'),
        ('exchanger', 'Exchanger'),
    ]
    
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
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='donor')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    address = models.TextField(blank=True)
    total_donations = models.PositiveIntegerField(default=0)
    completed_transactions = models.PositiveIntegerField(default=0)
    
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
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.name} ({self.email})"
    
    @property
    def badge_level(self):
        if self.completed_transactions >= 50:
            return '🏅 Super Donor'
        elif self.completed_transactions >= 20:
            return '🌟 Regular Donor'
        elif self.completed_transactions >= 5:
            return '⭐ Beginner Donor'
        return '🆕 Newbie'
    @property
    def is_donor_user(self):
        return self.is_superuser or self.is_staff or self.role == 'donor'

