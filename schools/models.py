"""
Schools models - Multi-tenant school management
"""
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class School(models.Model):
    """School tenant model"""
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('rejected', 'Rejected'),
    ]

    name = models.CharField(max_length=200)
    subdomain = models.CharField(max_length=50, unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    logo = models.ImageField(upload_to='school_logos/', blank=True, null=True)
    theme_color = models.CharField(max_length=7, default='#4F46E5', help_text='Hex color code')
    motto = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_demo = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Subscription
    subscription_active = models.BooleanField(default=False)
    subscription_expires = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"https://{self.subdomain}.educore.com"

    def get_full_domain(self):
        return f"{self.subdomain}.educore.com"


class SchoolUser(models.Model):
    """Link between User and School with role"""
    ROLE_CHOICES = [
        ('headmaster', 'Headmaster'),
        ('admin', 'School Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('parent', 'Parent'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='school_memberships')
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='members')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'school']

    def __str__(self):
        return f"{self.user.username} - {self.school.name} ({self.role})"
