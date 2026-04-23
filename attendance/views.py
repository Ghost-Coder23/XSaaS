"""
Attendance views - Mark and view attendance
"""
from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from .models import AttendanceSession, AttendanceRecord
from .forms import AttendanceSessionForm
from academics.models import ClassSection, Student
from schools.models import SchoolUser


@login_required
def attendance_home(request):
    school = request.school
    school_user = SchoolUser.objects.filter(user=request.user, school=school).first()
    today = date.today()

    # For teachers: show their classes
    if school_user and school_user.role == 'teacher':
        classes = ClassSection.objects.filter(
            school=school,
            teacher_subjects__teacher=school_user
        ).distinct()
    else:
        classes = ClassSection.objects.filter(school=school)

    # Today's sessions
    today_sessions = AttendanceSession.objects.filter(
        school=school, date=today
    ).select_related('class_section', 'marked_by__user')

    # Recent sessions (last 7 days)
    recent_sessions = AttendanceSession.objects.filter(
        school=school,
        date__gte=today - timedelta(days=7)
    ).select_related('class_section').order_by('-date')[:20]

    context = {
        'classes': classes,
        'today_sessions': today_sessions,
        'recent_sessions': recent_sessions,
        'today': today,
    }
    return render(request, 'attendance/attendance_home.html', context)


@login_required
def mark_attendance(request, class_id):
    school = request.school
    school_user = SchoolUser.objects.filter(user=request.user, school=school).first()
    class_section = get_object_or_404(ClassSection, id=class_id, school=school)

    selected_date = request.GET.get('date', str(date.today()))
    try:
        selected_date = date.fromisoformat(selected_date)
    except ValueError:
        selected_date = date.today()

    # Get or create session
    session, created = AttendanceSession.objects.get_or_create(
        class_section=class_section,
        date=selected_date,
        defaults={'school': school, 'marked_by': school_user}
    )

    students = Student.objects.filter(
        current_class=class_section, school=school, is_active=True
    ).select_related('user').order_by('user__last_name', 'user__first_name')

    # Get existing records
    existing = {r.student_id: r for r in session.records.all()}

    if request.method == 'POST':
        with transaction.atomic():
            for student in students:
                status = request.POST.get(f'status_{student.id}', 'present')
                notes = request.POST.get(f'notes_{student.id}', '')
                record, _ = AttendanceRecord.objects.update_or_create(
                    session=session,
                    student=student,
                    defaults={'status': status, 'notes': notes}
                )
            session.is_finalized = True
            session.marked_by = school_user
            session.save()

            # Notify for absences
            from notifications.utils import notify_absences
            absences = [s for s in students if request.POST.get(f'status_{s.id}') == 'absent']
            notify_absences(school, session, absences)

        messages.success(request, f'Attendance saved for {class_section} on {selected_date}.')
        return redirect('attendance:home')

    # Build student-record pairs
    student_records = []
    for s in students:
        student_records.append({
            'student': s,
            'record': existing.get(s.id),
        })

    context = {
        'class_section': class_section,
        'session': session,
        'student_records': student_records,
        'selected_date': selected_date,
        'is_finalized': session.is_finalized,
    }
    return render(request, 'attendance/mark_attendance.html', context)


@login_required
def attendance_report(request):
    school = request.school
    class_id = request.GET.get('class')
    month = request.GET.get('month', date.today().month)
    year = request.GET.get('year', date.today().year)

    classes = ClassSection.objects.filter(school=school)
    sessions = []
    students = []
    matrix = {}

    if class_id:
        class_section = get_object_or_404(ClassSection, id=class_id, school=school)
        sessions = AttendanceSession.objects.filter(
            class_section=class_section,
            date__month=month,
            date__year=year
        ).order_by('date')
        students = Student.objects.filter(
            current_class=class_section, school=school, is_active=True
        ).select_related('user').order_by('user__last_name')

        for student in students:
            matrix[student.id] = {}
            for session in sessions:
                rec = session.records.filter(student=student).first()
                matrix[student.id][session.id] = rec.status if rec else '-'

    context = {
        'classes': classes,
        'sessions': sessions,
        'students': students,
        'matrix': matrix,
        'selected_class': int(class_id) if class_id else None,
        'month': int(month),
        'year': int(year),
    }
    return render(request, 'attendance/attendance_report.html', context)


@login_required
def session_detail(request, session_id):
    school = request.school
    session = get_object_or_404(AttendanceSession, id=session_id, school=school)
    records = session.records.select_related('student__user').order_by('student__user__last_name')
    context = {'session': session, 'records': records, 'summary': session.get_summary()}
    return render(request, 'attendance/session_detail.html', context)
