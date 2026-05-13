from django.core.management.base import BaseCommand
from django.db import transaction
from core.middleware import get_current_school
from schools.models import SchoolUser
from academics.models import Subject as AcademicSubject, ClassSection
from timetable.models import Subject, Teacher, SchoolClass


class Command(BaseCommand):
    help = 'Import subjects, teachers, and classes from the academics app'

    def add_arguments(self, parser):
        parser.add_argument(
            '--school-id',
            type=int,
            help='School ID to import data for (optional, uses current school if not specified)',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting import from academics app...')

        school = None
        if options['school_id']:
            from schools.models import School
            school = School.objects.filter(id=options['school_id']).first()
            if not school:
                self.stdout.write(self.style.ERROR(f'School with ID {options["school_id"]} not found'))
                return
        else:
            try:
                school = get_current_school()
            except:
                self.stdout.write(self.style.ERROR('No current school found. Please use --school-id'))
                return

        if not school:
            self.stdout.write(self.style.ERROR('No school specified'))
            return

        with transaction.atomic():
            # Import Subjects
            self.stdout.write(f'Importing subjects for {school.name}...')
            academic_subjects = AcademicSubject.objects.filter(school=school)
            subjects_created = 0
            for ac_subject in academic_subjects:
                subject, created = Subject.objects.get_or_create(
                    school=school,
                    code=ac_subject.code or ac_subject.name[:20],
                    defaults={
                        'name': ac_subject.name,
                        'periods_per_week': 5,
                        'color': '#6366f1',
                    }
                )
                if created:
                    subjects_created += 1
            self.stdout.write(self.style.SUCCESS(f'  Created {subjects_created} subjects'))

            # Import Teachers
            self.stdout.write(f'Importing teachers for {school.name}...')
            teacher_school_users = SchoolUser.objects.filter(school=school, role='teacher', is_active=True)
            teachers_created = 0
            for su in teacher_school_users:
                teacher, created = Teacher.objects.get_or_create(
                    school=school,
                    email=su.user.email,
                    defaults={
                        'name': su.user.get_full_name() or su.user.username,
                        'available_days': [1, 2, 3, 4, 5],
                        'max_periods_per_day': 6,
                    }
                )
                if created:
                    teachers_created += 1
            self.stdout.write(self.style.SUCCESS(f'  Created {teachers_created} teachers'))

            # Import Classes
            self.stdout.write(f'Importing classes for {school.name}...')
            class_sections = ClassSection.objects.filter(school=school)
            classes_created = 0
            for cs in class_sections:
                class_name = f"{cs.class_level.name} {cs.section_name}"
                school_class, created = SchoolClass.objects.get_or_create(
                    school=school,
                    class_name=class_name,
                    defaults={
                        'grade_level': cs.class_level.order or 1,
                        'section': cs.section_name,
                    }
                )
                if created:
                    classes_created += 1
            self.stdout.write(self.style.SUCCESS(f'  Created {classes_created} classes'))

        self.stdout.write(self.style.SUCCESS('\nImport completed successfully!'))
