"""Results URL configuration"""
from django.urls import path
from . import views

app_name = 'results'

urlpatterns = [
    # Terms
    path('terms/', views.TermListView.as_view(), name='term_list'),
    path('terms/add/', views.TermCreateView.as_view(), name='term_add'),


    # Grade Scales
    path('grade-scales/', views.GradeScaleListView.as_view(), name='grade_scale_list'),
    path('grade-scales/add/', views.GradeScaleCreateView.as_view(), name='grade_scale_add'),
    path('grade-scales/<int:pk>/edit/', views.GradeScaleUpdateView.as_view(), name='grade_scale_edit'),
    path('grade-scales/<int:pk>/delete/', views.GradeScaleDeleteView.as_view(), name='grade_scale_delete'),

    # Result Entry
    path('entry/', views.ResultEntryView.as_view(), name='result_entry'),

    path('entry/bulk/', views.ResultEntryView.as_view(), name='bulk_entry'),

    # Approvals
    path('pending-approvals/', views.PendingApprovalsView.as_view(), name='pending_approvals'),
    path('approve-all/', views.approve_all_results, name='approve_all'),

    # Student Results
    path('student/<int:pk>/', views.StudentResultsView.as_view(), name='student_results'),
]
