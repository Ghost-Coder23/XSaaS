from django.contrib import admin
from .models import Subject, Teacher, Classroom, SchoolClass, Period, Timetable, TimetableEntry


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'periods_per_week', 'color']
    search_fields = ['name', 'code']


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'max_periods_per_day']
    search_fields = ['name', 'email']
    filter_horizontal = ['subjects']


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ['room_name', 'capacity', 'room_type']
    search_fields = ['room_name']


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ['class_name', 'grade_level', 'section', 'class_teacher']
    search_fields = ['class_name']


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ['label', 'start_time', 'end_time', 'is_break', 'order']
    ordering = ['order']


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ['school_class', 'academic_year', 'term', 'published', 'created_at']
    list_filter = ['published', 'term']
    search_fields = ['school_class__class_name', 'academic_year']


@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display = ['timetable', 'day_of_week', 'period', 'subject', 'teacher', 'classroom']
    list_filter = ['day_of_week']
    search_fields = ['subject__name', 'teacher__name']
