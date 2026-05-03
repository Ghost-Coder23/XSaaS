"""Analytics URL configuration"""
from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/attendance/', views.api_chart_attendance, name='api_attendance'),
    path('api/fees/', views.api_chart_fees, name='api_fees'),
]
