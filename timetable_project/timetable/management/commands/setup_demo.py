"""
Management command: python manage.py setup_demo

Creates a superuser (admin/admin) and seeds sample data so the app
is immediately usable after installation.
"""
import os
import django
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create demo superuser and seed sample school data'

    def handle(self, *args, **options):
        from timetable.models import Subject, Teacher, Classroom, SchoolClass, Period

        # ── Superuser ─────────────────────────────────────────────────────
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@school.edu', 'admin')
            self.stdout.write(self.style.SUCCESS('✓ Superuser created  (username: admin  password: admin)'))
        else:
            self.stdout.write('  Superuser already exists, skipping.')

        # ── Subjects ──────────────────────────────────────────────────────
        subjects_data = [
            ('Mathematics',      'MATH', 5, '#6366f1'),
            ('English',          'ENG',  4, '#10b981'),
            ('Physics',          'PHY',  3, '#f59e0b'),
            ('Chemistry',        'CHEM', 3, '#ef4444'),
            ('Biology',          'BIO',  3, '#8b5cf6'),
            ('History',          'HIST', 2, '#06b6d4'),
            ('Geography',        'GEO',  2, '#84cc16'),
            ('Computer Science', 'CS',   3, '#f97316'),
            ('Physical Education','PE',  2, '#ec4899'),
            ('Art',              'ART',  2, '#a78bfa'),
        ]
        subjects = {}
        for name, code, ppw, color in subjects_data:
            s, created = Subject.objects.get_or_create(
                code=code,
                defaults={'name': name, 'periods_per_week': ppw, 'color': color}
            )
            subjects[code] = s
        self.stdout.write(self.style.SUCCESS(f'✓ {len(subjects_data)} subjects ready'))

        # ── Periods ───────────────────────────────────────────────────────
        periods_data = [
            ('Period 1',  '07:30', '08:20', False, 1),
            ('Period 2',  '08:20', '09:10', False, 2),
            ('Break',     '09:10', '09:30', True,  3),
            ('Period 3',  '09:30', '10:20', False, 4),
            ('Period 4',  '10:20', '11:10', False, 5),
            ('Lunch',     '11:10', '11:50', True,  6),
            ('Period 5',  '11:50', '12:40', False, 7),
            ('Period 6',  '12:40', '13:30', False, 8),
            ('Period 7',  '13:30', '14:20', False, 9),
        ]
        for label, start, end, is_break, order in periods_data:
            Period.objects.get_or_create(
                label=label,
                defaults={
                    'start_time': start, 'end_time': end,
                    'is_break': is_break, 'order': order
                }
            )
        self.stdout.write(self.style.SUCCESS(f'✓ {len(periods_data)} periods ready'))

        # ── Classrooms ────────────────────────────────────────────────────
        rooms_data = [
            ('Room 101', 35, 'standard'), ('Room 102', 35, 'standard'),
            ('Room 103', 30, 'standard'), ('Room 201', 30, 'standard'),
            ('Room 202', 35, 'standard'), ('Science Lab', 25, 'lab'),
            ('Computer Lab', 30, 'computer'), ('Gym', 60, 'gym'),
        ]
        for room_name, cap, rtype in rooms_data:
            Classroom.objects.get_or_create(
                room_name=room_name, defaults={'capacity': cap, 'room_type': rtype}
            )
        self.stdout.write(self.style.SUCCESS(f'✓ {len(rooms_data)} classrooms ready'))

        # ── Teachers ──────────────────────────────────────────────────────
        teachers_data = [
            ('Alice Moyo',    'alice@school.edu',  ['MATH', 'CS'],       6),
            ('Bob Chikwanda', 'bob@school.edu',    ['ENG'],              5),
            ('Carol Dube',    'carol@school.edu',  ['PHY', 'MATH'],      6),
            ('David Mwale',   'david@school.edu',  ['CHEM', 'BIO'],      6),
            ('Eve Zimba',     'eve@school.edu',    ['HIST', 'GEO'],      5),
            ('Frank Banda',   'frank@school.edu',  ['CS'],               4),
            ('Grace Phiri',   'grace@school.edu',  ['PE', 'ART'],        5),
        ]
        for name, email, subject_codes, max_periods in teachers_data:
            teacher, _ = Teacher.objects.get_or_create(
                email=email,
                defaults={
                    'name': name,
                    'available_days': [1, 2, 3, 4, 5],
                    'max_periods_per_day': max_periods,
                }
            )
            teacher.subjects.set([subjects[c] for c in subject_codes if c in subjects])
        self.stdout.write(self.style.SUCCESS(f'✓ {len(teachers_data)} teachers ready'))

        # ── School Classes ────────────────────────────────────────────────
        classes_data = [
            ('Grade 8A', 8, 'A'), ('Grade 8B', 8, 'B'),
            ('Grade 9A', 9, 'A'), ('Grade 9B', 9, 'B'),
            ('Grade 10A', 10, 'A'), ('Grade 10B', 10, 'B'),
            ('Grade 11A', 11, 'A'), ('Grade 12A', 12, 'A'),
        ]
        for class_name, grade, section in classes_data:
            SchoolClass.objects.get_or_create(
                class_name=class_name,
                defaults={'grade_level': grade, 'section': section}
            )
        self.stdout.write(self.style.SUCCESS(f'✓ {len(classes_data)} school classes ready'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('════════════════════════════════════'))
        self.stdout.write(self.style.SUCCESS('  Demo setup complete!'))
        self.stdout.write(self.style.SUCCESS('  Login: admin / admin'))
        self.stdout.write(self.style.SUCCESS('  Run:   python manage.py runserver'))
        self.stdout.write(self.style.SUCCESS('════════════════════════════════════'))
