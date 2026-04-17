"""Reports URL configuration"""
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('generate/<int:student_id>/<int:term_id>/', views.generate_report_card, name='generate'),
    path('download/<int:pk>/', views.download_report, name='download'),
    path('class/<int:class_id>/<int:term_id>/', views.generate_class_reports, name='generate_class'),
]
