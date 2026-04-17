"""Attendance URL configuration"""
from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.attendance_home, name='home'),
    path('mark/<int:class_id>/', views.mark_attendance, name='mark'),
    path('report/', views.attendance_report, name='report'),
    path('session/<int:session_id>/', views.session_detail, name='session_detail'),
    path('api/sync/', views.api_sync_attendance, name='api_sync'),
]
