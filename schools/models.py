"""
Schools models - Multi-tenant school management
"""
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from core.models import TenantManager


class School(models.Model):
    """School tenant model"""
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('rejected', 'Rejected'),
    ]

    name = models.CharField(max_length=200)
    subdomain = models.CharField(max_length=50, unique=True, db_index=True)
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
        return f"https://{self.subdomain}.academialink.co.zw"

    def get_full_domain(self):
        return f"{self.subdomain}.academialink.co.zw"


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
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='members', db_index=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    signature = models.ImageField(upload_to='signatures/', blank=True, null=True)

    class Meta:
        unique_together = ['user', 'school']

    def __str__(self):
        return f"{self.user.username} - {self.school.name} ({self.role})"


class GalleryItem(models.Model):
    """Gallery item (image or video) for global showcase or specific school"""
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='gallery_items', null=True, blank=True, help_text="Leave blank for global showcase")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default='image')
    image = models.ImageField(upload_to='gallery/images/', blank=True, null=True, help_text="Upload if media type is Image")
    video_url = models.URLField(blank=True, null=True, help_text="YouTube or Vimeo URL if media type is Video")
    is_featured = models.BooleanField(default=False, help_text="Show on the home page")
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager() # Default to standard manager for global showcase
    tenant_objects = TenantManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        school_name = self.school.name if self.school else "Global Showcase"
        return f"{self.title} ({self.media_type}) - {school_name}"
