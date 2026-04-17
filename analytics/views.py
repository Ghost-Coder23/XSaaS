"""
Analytics views - Role-specific dashboards with real data
"""
from datetime import date, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Sum, Q
from django.http import JsonResponse

from schools.models import SchoolUser, School
from academics.models import Student, ClassSection, AcademicYear
from results.models import StudentResult, TermSummary, Term
from attendance.models import AttendanceSession, AttendanceRecord
from fees.models import FeeInvoice, FeePayment
from notifications.models import Notification


@login_required
def dashboard(request):
    school = request.school
    if not school:
        return redirect('home')
    try:
        membership = SchoolUser.objects.get(user=request.user, school=school, is_active=True)
    except SchoolUser.DoesNotExist:
        return redirect('home')

    role = membership.role
    if role == 'headmaster':
        return headmaster_dashboard(request, school, membership)
    elif role == 'admin':
        return admin_dashboard(request, school, membership)
    elif role == 'teacher':
        return teacher_dashboard(request, school, membership)
    elif role == 'parent':
        return parent_dashboard(request, school, membership)
    elif role == 'student':
        return student_dashboard(request, school, membership)
    return redirect('home')


def headmaster_dashboard(request, school, membership):
    today = date.today()
    current_term = Term.objects.filter(academic_year__school=school, is_current=True).first()
    current_year = AcademicYear.objects.filter(school=school, is_current=True).first()

    total_students = Student.objects.filter(school=school, is_active=True).count()
    total_teachers = SchoolUser.objects.filter(school=school, role='teacher', is_active=True).count()
    total_classes = ClassSection.objects.filter(school=school).count()
    pending_approvals = StudentResult.objects.filter(class_section__school=school, status='submitted').count()

    # Attendance today
    today_sessions = AttendanceSession.objects.filter(school=school, date=today)
    today_present = AttendanceRecord.objects.filter(session__in=today_sessions, status='present').count()
    today_absent = AttendanceRecord.objects.filter(session__in=today_sessions, status='absent').count()
    today_total = today_present + today_absent
    today_attendance_pct = round((today_present / today_total) * 100, 1) if today_total > 0 else 0

    # Attendance this week
    week_start = today - timedelta(days=today.weekday())
    week_sessions = AttendanceSession.objects.filter(school=school, date__gte=week_start, date__lte=today)
    week_present = AttendanceRecord.objects.filter(session__in=week_sessions, status='present').count()
    week_total = AttendanceRecord.objects.filter(session__in=week_sessions).count()
    week_attendance_pct = round((week_present / week_total) * 100, 1) if week_total > 0 else 0

    # Fee summary
    total_invoiced = FeeInvoice.objects.filter(school=school).aggregate(t=Sum('amount'))['t'] or 0
    total_collected = FeeInvoice.objects.filter(school=school).aggregate(t=Sum('amount_paid'))['t'] or 0
    collection_pct = round((total_collected / total_invoiced) * 100, 1) if total_invoiced > 0 else 0
    overdue_count = FeeInvoice.objects.filter(school=school, status__in=['unpaid','partial'], due_date__lt=today).count()

    # At-risk students (attendance < 80% this month)
    month_start = today.replace(day=1)
    at_risk_ids = []
    for student in Student.objects.filter(school=school, is_active=True):
        records = AttendanceRecord.objects.filter(
            student=student, session__date__gte=month_start, session__date__lte=today
        )
        total = records.count()
        if total >= 5:
            present = records.filter(status='present').count()
            pct = (present / total) * 100
            if pct < 80:
                at_risk_ids.append((student, round(pct, 1)))
    at_risk = sorted(at_risk_ids, key=lambda x: x[1])[:10]

    # Class performance (term summaries)
    class_performance = []
    if current_term:
        for cs in ClassSection.objects.filter(school=school):
            avg = TermSummary.objects.filter(class_section=cs, term=current_term).aggregate(a=Avg('average'))['a']
            if avg:
                class_performance.append({'class': cs, 'average': round(avg, 1)})
        class_performance.sort(key=lambda x: x['average'], reverse=True)

    # Recent results pending
    recent_pending = StudentResult.objects.filter(
        class_section__school=school, status='submitted'
    ).select_related('student__user', 'subject', 'term').order_by('-updated_at')[:8]

    # Notifications
    unread_notifications = Notification.objects.filter(
        recipient=request.user, school=school, is_read=False
    ).order_by('-created_at')[:5]

    context = {
        'role': 'headmaster',
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_classes': total_classes,
        'pending_approvals': pending_approvals,
        'today_attendance_pct': today_attendance_pct,
        'today_present': today_present,
        'today_absent': today_absent,
        'week_attendance_pct': week_attendance_pct,
        'total_invoiced': total_invoiced,
        'total_collected': total_collected,
        'collection_pct': collection_pct,
        'overdue_count': overdue_count,
        'at_risk': at_risk,
        'class_performance': class_performance,
        'recent_pending': recent_pending,
        'current_term': current_term,
        'unread_notifications': unread_notifications,
        'today': today,
    }
    return render(request, 'analytics/dashboard_headmaster.html', context)


def admin_dashboard(request, school, membership):
    today = date.today()
    current_term = Term.objects.filter(academic_year__school=school, is_current=True).first()

    total_students = Student.objects.filter(school=school, is_active=True).count()
    total_teachers = SchoolUser.objects.filter(school=school, role='teacher', is_active=True).count()
    total_parents = SchoolUser.objects.filter(school=school, role='parent', is_active=True).count()
    total_classes = ClassSection.objects.filter(school=school).count()

    # Fee overview
    total_invoiced = FeeInvoice.objects.filter(school=school).aggregate(t=Sum('amount'))['t'] or 0
    total_paid = FeeInvoice.objects.filter(school=school).aggregate(t=Sum('amount_paid'))['t'] or 0
    outstanding = total_invoiced - total_paid
    unpaid_invoices = FeeInvoice.objects.filter(school=school, status='unpaid').count()
    recent_invoices = FeeInvoice.objects.filter(school=school).select_related(
        'student__user'
    ).order_by('-created_at')[:8]

    # Attendance today
    today_sessions = AttendanceSession.objects.filter(school=school, date=today)
    classes_marked = today_sessions.filter(is_finalized=True).count()
    classes_not_marked = total_classes - classes_marked

    # Students per class
    classes_data = []
    for cs in ClassSection.objects.filter(school=school).select_related('class_level'):
        count = Student.objects.filter(current_class=cs, school=school, is_active=True).count()
        classes_data.append({'class': cs, 'count': count})

    unread_notifications = Notification.objects.filter(
        recipient=request.user, school=school, is_read=False
    ).order_by('-created_at')[:5]

    context = {
        'role': 'admin',
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_parents': total_parents,
        'total_classes': total_classes,
        'total_invoiced': total_invoiced,
        'total_paid': total_paid,
        'outstanding': outstanding,
        'unpaid_invoices': unpaid_invoices,
        'recent_invoices': recent_invoices,
        'classes_marked_today': classes_marked,
        'classes_not_marked': classes_not_marked,
        'classes_data': classes_data,
        'current_term': current_term,
        'unread_notifications': unread_notifications,
        'today': today,
    }
    return render(request, 'analytics/dashboard_admin.html', context)


def teacher_dashboard(request, school, membership):
    today = date.today()
    from academics.models import TeacherSubjectAssignment

    assignments = TeacherSubjectAssignment.objects.filter(
        teacher=membership, class_section__school=school
    ).select_related('subject', 'class_section__class_level')

    my_classes = list({a.class_section for a in assignments})

    # Today's attendance status per class
    class_attendance = []
    for cs in my_classes:
        session = AttendanceSession.objects.filter(class_section=cs, date=today).first()
        student_count = Student.objects.filter(current_class=cs, school=school, is_active=True).count()
        class_attendance.append({
            'class': cs,
            'session': session,
            'marked': session is not None and session.is_finalized,
            'student_count': student_count,
        })

    # Pending result entry
    current_term = Term.objects.filter(academic_year__school=school, is_current=True).first()
    pending_entry = []
    if current_term:
        for a in assignments:
            entered = StudentResult.objects.filter(
                class_section=a.class_section,
                subject=a.subject,
                term=current_term
            ).count()
            total_students = Student.objects.filter(
                current_class=a.class_section, school=school, is_active=True
            ).count()
            pending_entry.append({
                'assignment': a,
                'entered': entered,
                'total': total_students,
                'complete': entered >= total_students and total_students > 0,
            })

    # Class averages for my subjects
    class_averages = []
    if current_term:
        for a in assignments:
            avg = StudentResult.objects.filter(
                class_section=a.class_section,
                subject=a.subject,
                term=current_term,
                status__in=['approved', 'locked']
            ).aggregate(a=Avg('total_score'))['a']
            if avg:
                class_averages.append({
                    'class': a.class_section,
                    'subject': a.subject,
                    'average': round(avg, 1),
                })

    unread_notifications = Notification.objects.filter(
        recipient=request.user, school=school, is_read=False
    ).order_by('-created_at')[:5]

    context = {
        'role': 'teacher',
        'assignments': assignments,
        'class_attendance': class_attendance,
        'pending_entry': pending_entry,
        'class_averages': class_averages,
        'current_term': current_term,
        'unread_notifications': unread_notifications,
        'today': today,
    }
    return render(request, 'analytics/dashboard_teacher.html', context)


def parent_dashboard(request, school, membership):
    today = date.today()
    children = Student.objects.filter(
        school=school, parent_email=request.user.email, is_active=True
    ).select_related('user', 'current_class')

    children_data = []
    for child in children:
        # Attendance this month
        month_start = today.replace(day=1)
        records = AttendanceRecord.objects.filter(
            student=child, session__date__gte=month_start, session__date__lte=today
        )
        att_total = records.count()
        att_present = records.filter(status='present').count()
        att_pct = round((att_present / att_total) * 100, 1) if att_total > 0 else None

        # Latest term results
        current_term = Term.objects.filter(academic_year__school=school, is_current=True).first()
        latest_summary = TermSummary.objects.filter(student=child).select_related('term').order_by('-term__term_number').first()
        latest_results = []
        if current_term:
            latest_results = StudentResult.objects.filter(
                student=child, term=current_term, status__in=['approved', 'locked']
            ).select_related('subject').order_by('subject__name')

        # Fee balance
        invoices = FeeInvoice.objects.filter(student=child)
        total_owed = invoices.aggregate(t=Sum('amount'))['t'] or 0
        total_paid_amt = invoices.aggregate(t=Sum('amount_paid'))['t'] or 0
        balance = total_owed - total_paid_amt

        children_data.append({
            'student': child,
            'att_pct': att_pct,
            'att_present': att_present,
            'att_total': att_total,
            'latest_summary': latest_summary,
            'latest_results': latest_results,
            'fee_balance': balance,
            'current_term': current_term,
        })

    unread_notifications = Notification.objects.filter(
        recipient=request.user, school=school, is_read=False
    ).order_by('-created_at')[:5]

    context = {
        'role': 'parent',
        'children_data': children_data,
        'unread_notifications': unread_notifications,
        'today': today,
    }
    return render(request, 'analytics/dashboard_parent.html', context)


def student_dashboard(request, school, membership):
    today = date.today()
    try:
        student = Student.objects.get(user=request.user, school=school)
    except Student.DoesNotExist:
        return redirect('home')

    current_term = Term.objects.filter(academic_year__school=school, is_current=True).first()

    # Attendance this term
    term_records = []
    att_pct = None
    if current_term:
        term_records = AttendanceRecord.objects.filter(
            student=student,
            session__date__gte=current_term.start_date,
            session__date__lte=today
        )
        att_total = term_records.count()
        att_present = term_records.filter(status='present').count()
        att_pct = round((att_present / att_total) * 100, 1) if att_total > 0 else None

    # Results
    current_results = []
    term_summaries = TermSummary.objects.filter(student=student).select_related('term').order_by('-term__term_number')
    if current_term:
        current_results = StudentResult.objects.filter(
            student=student, term=current_term, status__in=['approved', 'locked']
        ).select_related('subject').order_by('subject__name')

    # Fee balance
    invoices = FeeInvoice.objects.filter(student=student)
    total_owed = invoices.aggregate(t=Sum('amount'))['t'] or 0
    total_paid_amt = invoices.aggregate(t=Sum('amount_paid'))['t'] or 0
    fee_balance = total_owed - total_paid_amt

    unread_notifications = Notification.objects.filter(
        recipient=request.user, school=school, is_read=False
    ).order_by('-created_at')[:5]

    context = {
        'role': 'student',
        'student': student,
        'current_term': current_term,
        'current_results': current_results,
        'term_summaries': term_summaries,
        'att_pct': att_pct,
        'fee_balance': fee_balance,
        'unread_notifications': unread_notifications,
        'today': today,
    }
    return render(request, 'analytics/dashboard_student.html', context)


@login_required
def api_chart_attendance(request):
    """JSON: last 7 days school attendance %"""
    school = request.school
    today = date.today()
    data = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        sessions = AttendanceSession.objects.filter(school=school, date=d)
        present = AttendanceRecord.objects.filter(session__in=sessions, status='present').count()
        total = AttendanceRecord.objects.filter(session__in=sessions).count()
        pct = round((present / total) * 100, 1) if total > 0 else 0
        data.append({'date': str(d), 'pct': pct, 'present': present, 'total': total})
    return JsonResponse({'data': data})


@login_required
def api_chart_fees(request):
    """JSON: fee collection summary by month (last 6 months)"""
    school = request.school
    today = date.today()
    data = []
    for i in range(5, -1, -1):
        month = (today.month - i - 1) % 12 + 1
        year = today.year if today.month - i > 0 else today.year - 1
        collected = FeePayment.objects.filter(
            invoice__school=school,
            status='confirmed',
            payment_date__month=month,
            payment_date__year=year
        ).aggregate(t=Sum('amount'))['t'] or 0
        data.append({'month': f'{year}-{month:02d}', 'collected': float(collected)})
    return JsonResponse({'data': data})
