"""Academics URL configuration"""
from django.urls import path
from . import views

app_name = 'academics'

urlpatterns = [
    path('years/', views.AcademicYearListView.as_view(), name='academic_year_list'),
    path('years/add/', views.AcademicYearCreateView.as_view(), name='academic_year_add'),
    path('class-levels/', views.ClassLevelListView.as_view(), name='class_level_list'),
    path('class-levels/add/', views.ClassLevelCreateView.as_view(), name='class_level_add'),
    path('subjects/', views.SubjectListView.as_view(), name='subject_list'),
    path('subjects/add/', views.SubjectCreateView.as_view(), name='subject_add'),
    path('sections/', views.ClassSectionListView.as_view(), name='class_section_list'),
    path('sections/add/', views.ClassSectionCreateView.as_view(), name='class_section_add'),
    path('students/', views.StudentListView.as_view(), name='student_list'),
    path('students/add/', views.StudentCreateView.as_view(), name='student_add'),
    path('students/<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    path('teachers/', views.TeacherListView.as_view(), name='teacher_list'),
    path('teachers/add/', views.TeacherCreateView.as_view(), name='teacher_add'),
    path('assignments/', views.TeacherAssignmentListView.as_view(), name='teacher_assignment_list'),
    path('assignments/add/', views.TeacherAssignmentCreateView.as_view(), name='teacher_assignment_add'),
]
