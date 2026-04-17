from django.contrib import admin
from .models import AttendanceSession, AttendanceRecord

class AttendanceRecordInline(admin.TabularInline):
    model = AttendanceRecord
    extra = 0

@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ['class_section', 'date', 'is_finalized', 'marked_by']
    list_filter = ['school', 'date', 'is_finalized']
    inlines = [AttendanceRecordInline]

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['student', 'session', 'status']
    list_filter = ['status']
