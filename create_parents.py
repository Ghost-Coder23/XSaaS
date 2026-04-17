from django.contrib.auth.models import User
from schools.models import SchoolUser, School
from academics.models import Student
school = School.objects.get(subdomain='demo')
students = Student.objects.filter(school=school)
parents = []
for student in students:
    parent_email = student.parent_email
    p_user, created = User.objects.get_or_create(
        username=parent_email,
        defaults={
            'email': parent_email,
            'first_name': student.parent_name.split()[0],
            'last_name': student.parent_name.split()[-1] if len(student.parent_name.split()) > 1 else 'Parent',
            'is_active': True
        }
    )
    if created:
        p_user.set_password('parent123')
        p_user.save()
        print(f"Created {parent_email} / parent123")
    SchoolUser.objects.get_or_create(
        user=p_user, school=school,
        defaults={'role': 'parent', 'is_active': True}
    )
    parents.append(parent_email)
print("Parents ready:", parents)

