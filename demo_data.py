"""
Demo data setup script
Run with: python manage.py shell < demo_data.py
"""
from django.contrib.auth.models import User
from schools.models import School, SchoolUser
from academics.models import AcademicYear, ClassLevel, ClassSection, Subject, Student, TeacherSubjectAssignment
from results.models import Term, GradeScale
from datetime import date

# Create demo school
school, _ = School.objects.get_or_create(
    subdomain='demo',
    defaults={
        'name': 'Greenwood Academy',
        'email': 'admin@greenwood.edu',
        'phone': '+263 77 123 4567',
        'address': '123 Education Road, Harare',
        'motto': 'Excellence in Every Endeavour',
        'status': 'active',
        'subscription_active': True,
        'theme_color': '#4F46E5',
        'is_demo': True,
    }
)
print(f"School: {school.name}")

# Create headmaster
hm_user, created = User.objects.get_or_create(
    username='headmaster@greenwood.edu',
    defaults={
        'email': 'headmaster@greenwood.edu',
        'first_name': 'Alice',
        'last_name': 'Moyo',
        'is_active': True,
    }
)
if created:
    hm_user.set_password('demo1234')
    hm_user.save()

SchoolUser.objects.get_or_create(user=hm_user, school=school, defaults={'role': 'headmaster', 'is_active': True})
print(f"Headmaster: {hm_user.email} / demo1234")

# Create teacher
t_user, created = User.objects.get_or_create(
    username='teacher@greenwood.edu',
    defaults={'email': 'teacher@greenwood.edu', 'first_name': 'Bob', 'last_name': 'Ncube'}
)
if created:
    t_user.set_password('demo1234')
    t_user.save()
teacher_su, _ = SchoolUser.objects.get_or_create(user=t_user, school=school, defaults={'role': 'teacher', 'is_active': True})
print(f"Teacher: {t_user.email} / demo1234")

# Academic year & term
yr, _ = AcademicYear.objects.get_or_create(school=school, name='2024-2025', defaults={'start_date': date(2024,1,15), 'end_date': date(2024,11,30), 'is_current': True})
term, _ = Term.objects.get_or_create(academic_year=yr, term_number=1, defaults={'name': 'First Term', 'start_date': date(2024,1,15), 'end_date': date(2024,4,5), 'is_current': True})

# Grade scales
for g, mn, mx, desc in [('A',80,100,'Excellent'),('B',65,79,'Very Good'),('C',50,64,'Good'),('D',40,49,'Pass'),('F',0,39,'Fail')]:
    GradeScale.objects.get_or_create(school=school, grade=g, defaults={'min_score': mn, 'max_score': mx, 'description': desc})

# Class levels
grade7, _ = ClassLevel.objects.get_or_create(school=school, name='Grade 7', defaults={'order': 7})
grade6, _ = ClassLevel.objects.get_or_create(school=school, name='Grade 6', defaults={'order': 6})

# Sections
sec7a, _ = ClassSection.objects.get_or_create(school=school, class_level=grade7, section_name='A', academic_year=yr, defaults={'class_teacher': teacher_su})
sec6a, _ = ClassSection.objects.get_or_create(school=school, class_level=grade6, section_name='A', academic_year=yr)

# Subjects
subjects_data = ['Mathematics', 'English', 'Science', 'Social Studies', 'Shona']
subjects = []
for s in subjects_data:
    subj, _ = Subject.objects.get_or_create(school=school, name=s)
    subjects.append(subj)
    TeacherSubjectAssignment.objects.get_or_create(teacher=teacher_su, subject=subj, class_section=sec7a, academic_year=yr)

print(f"Created {len(subjects)} subjects")

# Create students
students_data = [
    ('Tafadzwa', 'Chirwa', 'M', '2024001'),
    ('Chipo', 'Dube', 'F', '2024002'),
    ('Takudzwa', 'Moyo', 'M', '2024003'),
    ('Simbai', 'Mhaka', 'F', '2024004'),
    ('Tatenda', 'Zulu', 'M', '2024005'),
]
from django.contrib.auth.models import User

for fname, lname, gender, adm in students_data:
    email = f'{adm}@greenwood.edu'
    u, created = User.objects.get_or_create(username=email, defaults={'email': email, 'first_name': fname, 'last_name': lname})
    if created:
        u.set_password('student1234')
        u.save()
    su, _ = SchoolUser.objects.get_or_create(user=u, school=school, defaults={'role': 'student', 'is_active': True})
    Student.objects.get_or_create(
        admission_number=adm,
        defaults={
            'user': u, 'school': school, 'school_user': su,
            'date_of_birth': date(2012, 3, 15),
            'gender': gender, 'address': 'Harare, Zimbabwe',
            'current_class': sec7a,
            'parent_name': f'Parent of {fname}',
            'parent_phone': '+263771234567',
            'parent_email': f'parent.{adm}@gmail.com',
        }
    )

print(f"Created {len(students_data)} students")
print("\n=== DEMO DATA READY ===")
print("School URL: http://localhost:8000 (or demo.localhost:8000 with subdomain routing)")
print("Headmaster login: headmaster@greenwood.edu / demo1234")
print("Teacher login:    teacher@greenwood.edu / demo1234")
