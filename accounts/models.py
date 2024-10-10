# library_management_system/accounts/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class CustomUser(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    This model adds fields specific to library users.
    """
    ADMIN = 'admin'
    MEMBER = 'member'
    ROLES = [(ADMIN, 'Admin'), (MEMBER, 'Member')]
    
    date_of_membership = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    role = models.CharField(max_length=20, choices=ROLES, default=MEMBER)
    email_notifications = models.BooleanField(default=True)

    class Meta:
        ordering = ['id']
        indexes = [
                models.Index(fields=['username']), # For faster username searches
                models.Index(fields=['email']) # For faster email searches
            ]

    def __str__(self):
        return self.username