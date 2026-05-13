"""
Timetable Generation Engine

Generates conflict-free timetable entries using a constraint-satisfaction
approach with randomised backtracking. Mirrors the TypeScript original logic.
"""
import random
import logging
from dataclasses import dataclass, field
from typing import List, Optional
from django.db import transaction

logger = logging.getLogger(__name__)

WEEKDAYS = [1, 2, 3, 4, 5]  # Mon–Fri


@dataclass
class ConflictRecord:
    type: str
    description: str
    day_of_week: int = 0
    period_id: int = 0
    teacher_name: Optional[str] = None
    classroom_name: Optional[str] = None
    subject_name: Optional[str] = None

    def to_dict(self):
        return {
            'type': self.type,
            'description': self.description,
            'day_of_week': self.day_of_week,
            'period_id': self.period_id,
            'teacher_name': self.teacher_name,
            'classroom_name': self.classroom_name,
            'subject_name': self.subject_name,
        }


@dataclass
class GenerationOutcome:
    success: bool
    entries_created: int
    conflicts: List[ConflictRecord] = field(default_factory=list)
    message: Optional[str] = None

    def to_dict(self):
        return {
            'success': self.success,
            'entries_created': self.entries_created,
            'conflicts': [c.to_dict() for c in self.conflicts],
            'message': self.message,
        }


def generate_timetable(timetable_id: int) -> GenerationOutcome:
    """
    Generate timetable entries for a given Timetable record.
    Clears existing entries before generating new ones.
    """
    # Import here to avoid circular imports
    from timetable.models import (
        Timetable, TimetableEntry, Subject, Teacher,
        Classroom, Period
    )

    try:
        timetable = Timetable.objects.select_related('school_class').get(pk=timetable_id)
    except Timetable.DoesNotExist:
        return GenerationOutcome(success=False, entries_created=0, message="Timetable not found")

    # Load all periods, separate teaching vs break
    all_periods = list(Period.objects.order_by('order', 'start_time'))
    teaching_periods = [p for p in all_periods if not p.is_break]

    if not teaching_periods:
        return GenerationOutcome(
            success=False, entries_created=0,
            message="No teaching periods defined. Please add periods first."
        )

    subjects = list(Subject.objects.all())
    if not subjects:
        return GenerationOutcome(
            success=False, entries_created=0,
            message="No subjects defined. Please add subjects first."
        )

    teachers = list(Teacher.objects.prefetch_related('subjects').all())
    if not teachers:
        return GenerationOutcome(
            success=False, entries_created=0,
            message="No teachers defined. Please add teachers first."
        )

    classrooms = list(Classroom.objects.all())
    if not classrooms:
        return GenerationOutcome(
            success=False, entries_created=0,
            message="No classrooms defined. Please add classrooms first."
        )

    # Build subject-id sets per teacher for quick lookup
    teacher_subject_ids = {t.id: set(t.subjects.values_list('id', flat=True)) for t in teachers}

    # Check feasibility
    total_slots = len(WEEKDAYS) * len(teaching_periods)
    total_required = sum(s.periods_per_week for s in subjects)
    if total_required > total_slots:
        return GenerationOutcome(
            success=False, entries_created=0,
            message=(
                f"Impossible schedule: {total_required} periods required but only "
                f"{total_slots} slots available ({len(WEEKDAYS)} days × {len(teaching_periods)} periods)."
            )
        )

    # Get entries from OTHER published timetables for cross-conflict checks
    other_entries = list(
        TimetableEntry.objects.filter(
            timetable__published=True
        ).exclude(timetable_id=timetable_id)
    )

    # Occupation maps: key = "day-period_id"
    teacher_occupied: dict[int, set] = {}   # teacher_id -> set of "day-period_id"
    classroom_occupied: dict[int, set] = {}  # classroom_id -> set of "day-period_id"
    teacher_day_count: dict[int, dict] = {}  # teacher_id -> {day: count}

    def _slot_key(day, period_id):
        return f"{day}-{period_id}"

    def _mark_teacher(teacher_id, day, period_id):
        key = _slot_key(day, period_id)
        teacher_occupied.setdefault(teacher_id, set()).add(key)
        teacher_day_count.setdefault(teacher_id, {})
        teacher_day_count[teacher_id][day] = teacher_day_count[teacher_id].get(day, 0) + 1

    def _mark_classroom(classroom_id, day, period_id):
        key = _slot_key(day, period_id)
        classroom_occupied.setdefault(classroom_id, set()).add(key)

    def _teacher_free(teacher_id, day, period_id):
        return _slot_key(day, period_id) not in teacher_occupied.get(teacher_id, set())

    def _classroom_free(classroom_id, day, period_id):
        return _slot_key(day, period_id) not in classroom_occupied.get(classroom_id, set())

    def _teacher_day_load(teacher_id, day):
        return teacher_day_count.get(teacher_id, {}).get(day, 0)

    # Pre-populate from other published timetables
    for entry in other_entries:
        _mark_teacher(entry.teacher_id, entry.day_of_week, entry.period_id)
        _mark_classroom(entry.classroom_id, entry.day_of_week, entry.period_id)

    # Build all available slots and shuffle
    all_slots = [{'day': d, 'period_id': p.id} for d in WEEKDAYS for p in teaching_periods]
    random.shuffle(all_slots)

    # Expand subject queue (one entry per period_per_week)
    subject_queue = []
    for s in subjects:
        for _ in range(s.periods_per_week):
            subject_queue.append(s)
    random.shuffle(subject_queue)

    slot_used: set = set()
    generated_entries = []
    conflicts: List[ConflictRecord] = []

    subject_map = {s.id: s for s in subjects}

    for subject in subject_queue:
        eligible_teachers = [t for t in teachers if subject.id in teacher_subject_ids[t.id]]
        random.shuffle(eligible_teachers)

        if not eligible_teachers:
            conflicts.append(ConflictRecord(
                type='NO_TEACHER',
                description=(
                    f'No teacher assigned to teach "{subject.name}". '
                    f'Assign at least one teacher to this subject.'
                ),
                subject_name=subject.name,
            ))
            continue

        placed = False

        for slot in all_slots:
            slot_key = _slot_key(slot['day'], slot['period_id'])
            if slot_key in slot_used:
                continue

            for teacher in eligible_teachers:
                avail = teacher.available_days or [1, 2, 3, 4, 5]
                if slot['day'] not in avail:
                    continue
                if not _teacher_free(teacher.id, slot['day'], slot['period_id']):
                    continue
                if _teacher_day_load(teacher.id, slot['day']) >= teacher.max_periods_per_day:
                    continue

                available_classrooms = list(classrooms)
                random.shuffle(available_classrooms)
                for classroom in available_classrooms:
                    if not _classroom_free(classroom.id, slot['day'], slot['period_id']):
                        continue

                    generated_entries.append({
                        'timetable_id': timetable_id,
                        'day_of_week': slot['day'],
                        'period_id': slot['period_id'],
                        'subject_id': subject.id,
                        'teacher_id': teacher.id,
                        'classroom_id': classroom.id,
                    })
                    slot_used.add(slot_key)
                    _mark_teacher(teacher.id, slot['day'], slot['period_id'])
                    _mark_classroom(classroom.id, slot['day'], slot['period_id'])
                    placed = True
                    break

                if placed:
                    break
            if placed:
                break

        if not placed:
            teacher_names = ', '.join(t.name for t in eligible_teachers)
            conflicts.append(ConflictRecord(
                type='UNPLACEABLE',
                description=(
                    f'Could not place "{subject.name}" — all available slots are occupied. '
                    f'Consider adding more periods or teachers.'
                ),
                teacher_name=teacher_names or None,
                subject_name=subject.name,
            ))

    # Bulk create entries in a transaction
    with transaction.atomic():
        TimetableEntry.objects.filter(timetable_id=timetable_id).delete()
        entries_to_create = [TimetableEntry(**e) for e in generated_entries]
        TimetableEntry.objects.bulk_create(entries_to_create)
        # Mark timetable as auto-generated
        Timetable.objects.filter(pk=timetable_id).update(generated_by='auto')

    logger.info(
        "Timetable %d generation complete: %d entries, %d conflicts",
        timetable_id, len(generated_entries), len(conflicts)
    )

    return GenerationOutcome(
        success=len(conflicts) == 0 or len(generated_entries) > 0,
        entries_created=len(generated_entries),
        conflicts=conflicts,
        message=(
            f"Successfully generated {len(generated_entries)} entries."
            if not conflicts else
            f"Generated {len(generated_entries)} entries with {len(conflicts)} conflict(s)."
        )
    )


def detect_conflicts(timetable_id: int) -> List[ConflictRecord]:
    """Detect conflicts in an existing timetable without modifying it."""
    from timetable.models import TimetableEntry

    entries = list(
        TimetableEntry.objects.filter(timetable_id=timetable_id)
        .select_related('teacher', 'classroom', 'subject', 'period')
    )

    conflicts = []

    # Teacher double-booking
    teacher_slots: dict = {}
    for entry in entries:
        key = f"{entry.teacher_id}-{entry.day_of_week}-{entry.period_id}"
        teacher_slots.setdefault(key, []).append(entry)

    for key, slot_entries in teacher_slots.items():
        if len(slot_entries) > 1:
            e = slot_entries[0]
            conflicts.append(ConflictRecord(
                type='TEACHER_CONFLICT',
                description=f'Teacher double-booked on {e.get_day_of_week_display()}, {e.period.label}',
                day_of_week=e.day_of_week,
                period_id=e.period_id,
                teacher_name=e.teacher.name,
            ))

    # Classroom double-booking
    classroom_slots: dict = {}
    for entry in entries:
        key = f"{entry.classroom_id}-{entry.day_of_week}-{entry.period_id}"
        classroom_slots.setdefault(key, []).append(entry)

    for key, slot_entries in classroom_slots.items():
        if len(slot_entries) > 1:
            e = slot_entries[0]
            conflicts.append(ConflictRecord(
                type='CLASSROOM_CONFLICT',
                description=f'Classroom double-booked on {e.get_day_of_week_display()}, {e.period.label}',
                day_of_week=e.day_of_week,
                period_id=e.period_id,
                classroom_name=e.classroom.room_name,
            ))

    return conflicts
