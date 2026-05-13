from django.urls import path
from . import views

app_name = 'timetable'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Subjects
    path('subjects/', views.subject_list, name='subjects'),
    path('api/subjects/', views.api_subjects, name='api-subjects'),
    path('api/subjects/create/', views.subject_create, name='subject-create'),
    path('api/subjects/<int:pk>/update/', views.subject_update, name='subject-update'),
    path('api/subjects/<int:pk>/delete/', views.subject_delete, name='subject-delete'),

    # Teachers
    path('teachers/', views.teacher_list, name='teachers'),
    path('api/teachers/', views.api_teachers, name='api-teachers'),
    path('api/teachers/create/', views.teacher_create, name='teacher-create'),
    path('api/teachers/<int:pk>/update/', views.teacher_update, name='teacher-update'),
    path('api/teachers/<int:pk>/delete/', views.teacher_delete, name='teacher-delete'),
    path('api/teachers/<int:pk>/schedule/', views.teacher_schedule, name='teacher-schedule'),

    # Classrooms
    path('classrooms/', views.classroom_list, name='classrooms'),
    path('api/classrooms/', views.api_classrooms, name='api-classrooms'),
    path('api/classrooms/create/', views.classroom_create, name='classroom-create'),
    path('api/classrooms/<int:pk>/update/', views.classroom_update, name='classroom-update'),
    path('api/classrooms/<int:pk>/delete/', views.classroom_delete, name='classroom-delete'),

    # Classes
    path('classes/', views.class_list, name='classes'),
    path('api/classes/', views.api_classes, name='api-classes'),
    path('api/classes/create/', views.class_create, name='class-create'),
    path('api/classes/<int:pk>/update/', views.class_update, name='class-update'),
    path('api/classes/<int:pk>/delete/', views.class_delete, name='class-delete'),

    # Periods
    path('periods/', views.period_list, name='periods'),
    path('api/periods/', views.api_periods, name='api-periods'),
    path('api/periods/create/', views.period_create, name='period-create'),
    path('api/periods/<int:pk>/update/', views.period_update, name='period-update'),
    path('api/periods/<int:pk>/delete/', views.period_delete, name='period-delete'),

    # Timetables
    path('timetables/', views.timetable_list, name='timetables'),
    path('timetables/<int:pk>/', views.timetable_view, name='timetable-view'),
    path('api/timetables/create/', views.timetable_create, name='timetable-create'),
    path('api/timetables/<int:pk>/delete/', views.timetable_delete, name='timetable-delete'),
    path('api/timetables/<int:pk>/generate/', views.timetable_generate, name='timetable-generate'),
    path('api/timetables/<int:pk>/publish/', views.timetable_publish, name='timetable-publish'),
    path('api/timetables/<int:pk>/unpublish/', views.timetable_unpublish, name='timetable-unpublish'),
    path('api/timetables/<int:pk>/clone/', views.timetable_clone, name='timetable-clone'),
    path('api/timetables/<int:pk>/conflicts/', views.timetable_conflicts, name='timetable-conflicts'),
    path('api/timetables/<int:pk>/entries/', views.timetable_entries, name='timetable-entries'),

    # Entries
    path('api/entries/create/', views.entry_create, name='entry-create'),
    path('api/entries/<int:pk>/update/', views.entry_update, name='entry-update'),
    path('api/entries/<int:pk>/delete/', views.entry_delete, name='entry-delete'),
    
    # Import from academics app
    path('api/import/', views.import_from_academics, name='import-from-academics'),
]
