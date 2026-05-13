import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db.models import Count, Q
from django.db import transaction

from .models import (
    Subject, Teacher, Classroom, SchoolClass,
    Period, Timetable, TimetableEntry
)
from .services.generator import generate_timetable, detect_conflicts


# ─── Dashboard ─────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    stats = {
        'subjects': Subject.objects.count(),
        'teachers': Teacher.objects.count(),
        'classrooms': Classroom.objects.count(),
        'classes': SchoolClass.objects.count(),
        'periods': Period.objects.filter(is_break=False).count(),
        'timetables': Timetable.objects.count(),
        'published': Timetable.objects.filter(published=True).count(),
    }
    recent_timetables = (
        Timetable.objects.select_related('school_class')
        .annotate(entry_count=Count('entries'))
        .order_by('-created_at')[:5]
    )
    return render(request, 'timetable/dashboard.html', {
        'stats': stats,
        'recent_timetables': recent_timetables,
    })


# ─── Subjects ──────────────────────────────────────────────────────────────

@login_required
def subject_list(request):
    subjects = Subject.objects.all()
    return render(request, 'timetable/subjects.html', {'subjects': subjects})


@login_required
@require_http_methods(["POST"])
def subject_create(request):
    data = json.loads(request.body)
    subject = Subject.objects.create(
        name=data['name'],
        code=data['code'],
        periods_per_week=int(data.get('periods_per_week', 1)),
        color=data.get('color', '#6366f1'),
    )
    return JsonResponse({'id': subject.id, 'name': subject.name, 'code': subject.code,
                         'periods_per_week': subject.periods_per_week, 'color': subject.color})


@login_required
@require_http_methods(["PUT"])
def subject_update(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    data = json.loads(request.body)
    subject.name = data.get('name', subject.name)
    subject.code = data.get('code', subject.code)
    subject.periods_per_week = int(data.get('periods_per_week', subject.periods_per_week))
    subject.color = data.get('color', subject.color)
    subject.save()
    return JsonResponse({'id': subject.id, 'name': subject.name, 'code': subject.code,
                         'periods_per_week': subject.periods_per_week, 'color': subject.color})


@login_required
@require_http_methods(["DELETE"])
def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    subject.delete()
    return JsonResponse({'success': True})


# ─── Teachers ──────────────────────────────────────────────────────────────

@login_required
def teacher_list(request):
    teachers = Teacher.objects.prefetch_related('subjects').all()
    subjects = Subject.objects.all()
    return render(request, 'timetable/teachers.html', {
        'teachers': teachers, 'subjects': subjects
    })


@login_required
@require_http_methods(["POST"])
def teacher_create(request):
    data = json.loads(request.body)
    available_days = data.get('available_days', [1, 2, 3, 4, 5])
    teacher = Teacher.objects.create(
        name=data['name'],
        email=data['email'],
        available_days=available_days,
        max_periods_per_day=int(data.get('max_periods_per_day', 6)),
    )
    subject_ids = data.get('subject_ids', [])
    if subject_ids:
        teacher.subjects.set(Subject.objects.filter(id__in=subject_ids))
    return JsonResponse({
        'id': teacher.id, 'name': teacher.name, 'email': teacher.email,
        'available_days': teacher.available_days,
        'max_periods_per_day': teacher.max_periods_per_day,
        'subject_ids': list(teacher.subjects.values_list('id', flat=True)),
    })


@login_required
@require_http_methods(["PUT"])
def teacher_update(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    data = json.loads(request.body)
    teacher.name = data.get('name', teacher.name)
    teacher.email = data.get('email', teacher.email)
    teacher.available_days = data.get('available_days', teacher.available_days)
    teacher.max_periods_per_day = int(data.get('max_periods_per_day', teacher.max_periods_per_day))
    teacher.save()
    if 'subject_ids' in data:
        teacher.subjects.set(Subject.objects.filter(id__in=data['subject_ids']))
    return JsonResponse({
        'id': teacher.id, 'name': teacher.name, 'email': teacher.email,
        'available_days': teacher.available_days,
        'max_periods_per_day': teacher.max_periods_per_day,
        'subject_ids': list(teacher.subjects.values_list('id', flat=True)),
    })


@login_required
@require_http_methods(["DELETE"])
def teacher_delete(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    teacher.delete()
    return JsonResponse({'success': True})


@login_required
def teacher_schedule(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    entries = (
        TimetableEntry.objects
        .filter(teacher=teacher, timetable__published=True)
        .select_related('period', 'subject', 'classroom', 'timetable__school_class')
        .order_by('day_of_week', 'period__order')
    )
    return JsonResponse({'teacher': teacher.name, 'entries': [
        {
            'day_of_week': e.day_of_week,
            'day_name': e.get_day_of_week_display(),
            'period_label': e.period.label,
            'period_start': str(e.period.start_time),
            'period_end': str(e.period.end_time),
            'subject_name': e.subject.name,
            'subject_color': e.subject.color,
            'classroom_name': e.classroom.room_name,
            'class_name': e.timetable.school_class.class_name,
        }
        for e in entries
    ]})


# ─── Classrooms ────────────────────────────────────────────────────────────

@login_required
def classroom_list(request):
    classrooms = Classroom.objects.all()
    return render(request, 'timetable/classrooms.html', {'classrooms': classrooms})


@login_required
@require_http_methods(["POST"])
def classroom_create(request):
    data = json.loads(request.body)
    classroom = Classroom.objects.create(
        room_name=data['room_name'],
        capacity=int(data.get('capacity', 30)),
        room_type=data.get('room_type', 'standard'),
    )
    return JsonResponse({
        'id': classroom.id, 'room_name': classroom.room_name,
        'capacity': classroom.capacity, 'room_type': classroom.room_type,
    })


@login_required
@require_http_methods(["PUT"])
def classroom_update(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)
    data = json.loads(request.body)
    classroom.room_name = data.get('room_name', classroom.room_name)
    classroom.capacity = int(data.get('capacity', classroom.capacity))
    classroom.room_type = data.get('room_type', classroom.room_type)
    classroom.save()
    return JsonResponse({
        'id': classroom.id, 'room_name': classroom.room_name,
        'capacity': classroom.capacity, 'room_type': classroom.room_type,
    })


@login_required
@require_http_methods(["DELETE"])
def classroom_delete(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)
    classroom.delete()
    return JsonResponse({'success': True})


# ─── Classes ───────────────────────────────────────────────────────────────

@login_required
def class_list(request):
    classes = SchoolClass.objects.select_related('class_teacher').all()
    teachers = Teacher.objects.all()
    return render(request, 'timetable/classes.html', {
        'classes': classes, 'teachers': teachers
    })


@login_required
@require_http_methods(["POST"])
def class_create(request):
    data = json.loads(request.body)
    school_class = SchoolClass.objects.create(
        class_name=data['class_name'],
        grade_level=int(data['grade_level']),
        section=data['section'],
        class_teacher_id=data.get('class_teacher_id') or None,
    )
    return JsonResponse({
        'id': school_class.id, 'class_name': school_class.class_name,
        'grade_level': school_class.grade_level, 'section': school_class.section,
        'class_teacher_id': school_class.class_teacher_id,
    })


@login_required
@require_http_methods(["PUT"])
def class_update(request, pk):
    school_class = get_object_or_404(SchoolClass, pk=pk)
    data = json.loads(request.body)
    school_class.class_name = data.get('class_name', school_class.class_name)
    school_class.grade_level = int(data.get('grade_level', school_class.grade_level))
    school_class.section = data.get('section', school_class.section)
    school_class.class_teacher_id = data.get('class_teacher_id') or None
    school_class.save()
    return JsonResponse({
        'id': school_class.id, 'class_name': school_class.class_name,
        'grade_level': school_class.grade_level, 'section': school_class.section,
        'class_teacher_id': school_class.class_teacher_id,
    })


@login_required
@require_http_methods(["DELETE"])
def class_delete(request, pk):
    school_class = get_object_or_404(SchoolClass, pk=pk)
    school_class.delete()
    return JsonResponse({'success': True})


# ─── Periods ───────────────────────────────────────────────────────────────

@login_required
def period_list(request):
    periods = Period.objects.all()
    return render(request, 'timetable/periods.html', {'periods': periods})


@login_required
@require_http_methods(["POST"])
def period_create(request):
    data = json.loads(request.body)
    period = Period.objects.create(
        start_time=data['start_time'],
        end_time=data['end_time'],
        label=data['label'],
        is_break=data.get('is_break', False),
        order=int(data.get('order', 0)),
    )
    return JsonResponse({
        'id': period.id, 'label': period.label,
        'start_time': str(period.start_time), 'end_time': str(period.end_time),
        'is_break': period.is_break, 'order': period.order,
    })


@login_required
@require_http_methods(["PUT"])
def period_update(request, pk):
    period = get_object_or_404(Period, pk=pk)
    data = json.loads(request.body)
    period.start_time = data.get('start_time', str(period.start_time))
    period.end_time = data.get('end_time', str(period.end_time))
    period.label = data.get('label', period.label)
    period.is_break = data.get('is_break', period.is_break)
    period.order = int(data.get('order', period.order))
    period.save()
    return JsonResponse({
        'id': period.id, 'label': period.label,
        'start_time': str(period.start_time), 'end_time': str(period.end_time),
        'is_break': period.is_break, 'order': period.order,
    })


@login_required
@require_http_methods(["DELETE"])
def period_delete(request, pk):
    period = get_object_or_404(Period, pk=pk)
    period.delete()
    return JsonResponse({'success': True})


# ─── Timetables ────────────────────────────────────────────────────────────

@login_required
def timetable_list(request):
    timetables = (
        Timetable.objects.select_related('school_class')
        .annotate(entry_count=Count('entries'))
        .order_by('-created_at')
    )
    classes = SchoolClass.objects.all()
    return render(request, 'timetable/timetables.html', {
        'timetables': timetables, 'classes': classes
    })


@login_required
@require_http_methods(["POST"])
def timetable_create(request):
    data = json.loads(request.body)
    timetable = Timetable.objects.create(
        school_class_id=data['school_class_id'],
        academic_year=data['academic_year'],
        term=data['term'],
        created_by=request.user,
    )
    return JsonResponse({
        'id': timetable.id,
        'class_name': timetable.school_class.class_name,
        'academic_year': timetable.academic_year,
        'term': timetable.term,
        'published': timetable.published,
        'entry_count': 0,
    })


@login_required
@require_http_methods(["DELETE"])
def timetable_delete(request, pk):
    timetable = get_object_or_404(Timetable, pk=pk)
    timetable.delete()
    return JsonResponse({'success': True})


@login_required
@require_http_methods(["POST"])
def timetable_generate(request, pk):
    timetable = get_object_or_404(Timetable, pk=pk)
    outcome = generate_timetable(timetable.id)
    return JsonResponse(outcome.to_dict())


@login_required
@require_http_methods(["POST"])
def timetable_publish(request, pk):
    timetable = get_object_or_404(Timetable, pk=pk)
    timetable.published = True
    timetable.save()
    return JsonResponse({'success': True, 'published': True})


@login_required
@require_http_methods(["POST"])
def timetable_unpublish(request, pk):
    timetable = get_object_or_404(Timetable, pk=pk)
    timetable.published = False
    timetable.save()
    return JsonResponse({'success': True, 'published': False})


@login_required
@require_http_methods(["POST"])
def timetable_clone(request, pk):
    source = get_object_or_404(Timetable, pk=pk)
    data = json.loads(request.body)
    with transaction.atomic():
        cloned = Timetable.objects.create(
            school_class_id=data.get('school_class_id', source.school_class_id),
            academic_year=data['academic_year'],
            term=data['term'],
            published=False,
            created_by=request.user,
        )
        source_entries = source.entries.all()
        TimetableEntry.objects.bulk_create([
            TimetableEntry(
                timetable=cloned,
                day_of_week=e.day_of_week,
                period_id=e.period_id,
                subject_id=e.subject_id,
                teacher_id=e.teacher_id,
                classroom_id=e.classroom_id,
            )
            for e in source_entries
        ])
    return JsonResponse({
        'id': cloned.id,
        'class_name': cloned.school_class.class_name,
        'academic_year': cloned.academic_year,
        'term': cloned.term,
        'published': cloned.published,
        'entry_count': source_entries.count(),
    })


@login_required
def timetable_conflicts(request, pk):
    timetable = get_object_or_404(Timetable, pk=pk)
    conflicts = detect_conflicts(timetable.id)
    return JsonResponse({'conflicts': [c.to_dict() for c in conflicts]})


@login_required
def timetable_view(request, pk):
    timetable = get_object_or_404(
        Timetable.objects.select_related('school_class').annotate(entry_count=Count('entries')),
        pk=pk
    )
    periods = Period.objects.order_by('order', 'start_time')
    entries = (
        TimetableEntry.objects.filter(timetable=timetable)
        .select_related('period', 'subject', 'teacher', 'classroom')
    )

    # Build grid: {day: {period_id: entry}}
    grid = {}
    days = [1, 2, 3, 4, 5]
    day_names = {1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday'}
    for day in days:
        grid[day] = {}
    for entry in entries:
        grid[entry.day_of_week][entry.period_id] = entry

    return render(request, 'timetable/timetable_view.html', {
        'timetable': timetable,
        'periods': periods,
        'grid': grid,
        'days': days,
        'day_names': day_names,
    })


# ─── Timetable Entries (CRUD) ──────────────────────────────────────────────

@login_required
def timetable_entries(request, pk):
    """Return all entries for a timetable as JSON."""
    timetable = get_object_or_404(Timetable, pk=pk)
    entries = (
        TimetableEntry.objects.filter(timetable=timetable)
        .select_related('period', 'subject', 'teacher', 'classroom')
    )
    return JsonResponse({'entries': [
        {
            'id': e.id,
            'day_of_week': e.day_of_week,
            'day_name': e.get_day_of_week_display(),
            'period_id': e.period_id,
            'period_label': e.period.label,
            'period_start': str(e.period.start_time),
            'period_end': str(e.period.end_time),
            'subject_id': e.subject_id,
            'subject_name': e.subject.name,
            'subject_color': e.subject.color,
            'teacher_id': e.teacher_id,
            'teacher_name': e.teacher.name,
            'classroom_id': e.classroom_id,
            'classroom_name': e.classroom.room_name,
        }
        for e in entries
    ]})


@login_required
@require_http_methods(["POST"])
def entry_create(request):
    data = json.loads(request.body)
    # Conflict checks
    if TimetableEntry.objects.filter(
        teacher_id=data['teacher_id'],
        day_of_week=data['day_of_week'],
        period_id=data['period_id']
    ).exists():
        return JsonResponse({'error': 'Teacher is already assigned at this period'}, status=400)

    if TimetableEntry.objects.filter(
        classroom_id=data['classroom_id'],
        day_of_week=data['day_of_week'],
        period_id=data['period_id']
    ).exists():
        return JsonResponse({'error': 'Classroom is already booked at this period'}, status=400)

    entry = TimetableEntry.objects.create(
        timetable_id=data['timetable_id'],
        day_of_week=data['day_of_week'],
        period_id=data['period_id'],
        subject_id=data['subject_id'],
        teacher_id=data['teacher_id'],
        classroom_id=data['classroom_id'],
    )
    entry.refresh_from_db()
    e = TimetableEntry.objects.select_related('period', 'subject', 'teacher', 'classroom').get(pk=entry.pk)
    return JsonResponse({
        'id': e.id,
        'day_of_week': e.day_of_week,
        'period_label': e.period.label,
        'subject_name': e.subject.name,
        'subject_color': e.subject.color,
        'teacher_name': e.teacher.name,
        'classroom_name': e.classroom.room_name,
    }, status=201)


@login_required
@require_http_methods(["PUT"])
def entry_update(request, pk):
    entry = get_object_or_404(TimetableEntry, pk=pk)
    data = json.loads(request.body)

    target_teacher = data.get('teacher_id', entry.teacher_id)
    target_day = data.get('day_of_week', entry.day_of_week)
    target_period = data.get('period_id', entry.period_id)
    target_classroom = data.get('classroom_id', entry.classroom_id)

    conflict = TimetableEntry.objects.filter(
        teacher_id=target_teacher, day_of_week=target_day, period_id=target_period
    ).exclude(pk=pk).first()
    if conflict:
        return JsonResponse({'error': 'Teacher is already assigned at this period'}, status=400)

    for field, val in data.items():
        setattr(entry, field, val)
    entry.save()
    return JsonResponse({'success': True})


@login_required
@require_http_methods(["DELETE"])
def entry_delete(request, pk):
    entry = get_object_or_404(TimetableEntry, pk=pk)
    entry.delete()
    return JsonResponse({'success': True})


# ─── API: data endpoints ───────────────────────────────────────────────────

@login_required
def api_subjects(request):
    subjects = list(Subject.objects.values('id', 'name', 'code', 'periods_per_week', 'color'))
    return JsonResponse(subjects, safe=False)


@login_required
def api_teachers(request):
    teachers = Teacher.objects.prefetch_related('subjects').all()
    return JsonResponse([{
        'id': t.id, 'name': t.name, 'email': t.email,
        'available_days': t.available_days,
        'max_periods_per_day': t.max_periods_per_day,
        'subject_ids': list(t.subjects.values_list('id', flat=True)),
    } for t in teachers], safe=False)


@login_required
def api_classrooms(request):
    classrooms = list(Classroom.objects.values('id', 'room_name', 'capacity', 'room_type'))
    return JsonResponse(classrooms, safe=False)


@login_required
def api_classes(request):
    classes = list(SchoolClass.objects.values('id', 'class_name', 'grade_level', 'section', 'class_teacher_id'))
    return JsonResponse(classes, safe=False)


@login_required
def api_periods(request):
    periods = list(Period.objects.values('id', 'label', 'start_time', 'end_time', 'is_break', 'order'))
    # Convert time fields to string
    for p in periods:
        p['start_time'] = str(p['start_time'])
        p['end_time'] = str(p['end_time'])
    return JsonResponse(periods, safe=False)
