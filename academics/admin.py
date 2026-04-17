from django.contrib import admin
from .models import AcademicYear, ClassLevel, Subject, ClassSection, Student, TeacherSubjectAssignment

admin.site.register(AcademicYear)
admin.site.register(ClassLevel)
admin.site.register(Subject)
admin.site.register(ClassSection)
admin.site.register(Student)
admin.site.register(TeacherSubjectAssignment)
