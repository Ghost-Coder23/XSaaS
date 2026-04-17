from django.contrib import admin
from .models import Notification, SMSLog, Announcement

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'recipient', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'school']

@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ['recipient_phone', 'recipient_name', 'status', 'created_at']
    list_filter = ['status', 'school']

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'school', 'audience', 'is_active', 'created_at']
    list_filter = ['school', 'audience', 'is_active']
