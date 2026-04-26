from django.contrib import admin
from django.utils import timezone
from .models import (
    AcademicYear,
    ClassLevel,
    Subject,
    ClassSection,
    Student,
    ParentStudentLink,
    TeacherSubjectAssignment,
)

admin.site.register(AcademicYear)
admin.site.register(ClassLevel)
admin.site.register(Subject)
admin.site.register(ClassSection)

class StudentAdmin(admin.ModelAdmin):
    exclude = ('admission_number',)
    list_display = ('user', 'admission_number', 'school', 'current_class', 'is_active')
    search_fields = ('user__first_name', 'user__last_name', 'admission_number')
    list_filter = ('school', 'current_class', 'is_active')

    def save_model(self, request, obj, form, change):
        if not obj.admission_number:
            current_year = timezone.now().year
            last_student = Student.objects.filter(
                school=obj.school,
                admission_number__startswith=str(current_year)
            ).order_by('-admission_number').first()
            if last_student and last_student.admission_number[4:].isdigit():
                next_seq = int(last_student.admission_number[4:]) + 1
            else:
                next_seq = 1
            obj.admission_number = f"{current_year}{next_seq:03d}"
        super().save_model(request, obj, form, change)

admin.site.register(Student, StudentAdmin)

admin.site.register(ParentStudentLink)
admin.site.register(TeacherSubjectAssignment)
