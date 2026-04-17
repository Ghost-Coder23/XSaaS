"""Notifications URL configuration"""
from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='list'),
    path('unread/', views.unread_count, name='unread_count'),
    path('<int:pk>/read/', views.mark_read, name='mark_read'),
    path('announcements/', views.announcements, name='announcements'),
    path('announcements/create/', views.create_announcement, name='create_announcement'),
]
