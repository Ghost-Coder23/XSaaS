"""Reports URL configuration"""
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('generate/<uuid:student_id>/<uuid:term_id>/', views.generate_report_card, name='generate'),
    path('download/<uuid:pk>/', views.download_report, name='download'),
    path('class/<uuid:class_id>/<uuid:term_id>/', views.generate_class_reports, name='generate_class'),
]
