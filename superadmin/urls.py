"""Superadmin URL configuration"""
from django.urls import path
from . import views

app_name = 'superadmin'

urlpatterns = [
    path('', views.platform_dashboard, name='dashboard'),
    path('schools/', views.school_list, name='school_list'),
    path('schools/<int:school_id>/', views.school_detail, name='school_detail'),
    path('schools/<int:school_id>/approve/', views.approve_school, name='approve_school'),
    path('schools/<int:school_id>/suspend/', views.suspend_school, name='suspend_school'),
]
