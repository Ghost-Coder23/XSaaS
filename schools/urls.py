"""Schools URL configuration"""
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('settings/', views.SchoolSettingsView.as_view(), name='school_settings'),
    path('users/', views.UserManagementView.as_view(), name='user_management'),
    path('users/add/', views.add_school_user, name='add_school_user'),
    path('user/<int:pk>/edit/', views.school_user_edit, name='user_edit'),
    path('user/<int:pk>/deactivate/', views.school_user_deactivate, name='user_deactivate'),
    path('parent/register/', views.ParentRegistrationView.as_view(), name='parent_register'),
    path('upload-signature/', views.upload_signature, name='upload_signature'),
]
