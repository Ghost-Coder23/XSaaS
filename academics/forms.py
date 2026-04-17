"""Academics forms"""
from django import forms
from .models import (
    AcademicYear, ClassLevel, Subject, ClassSection, 
    Student, TeacherSubjectAssignment
)
from schools.models import SchoolUser


class AcademicYearForm(forms.ModelForm):
    class Meta:
        model = AcademicYear
        fields = ['name', 'start_date', 'end_date', 'is_current']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class ClassLevelForm(forms.ModelForm):
    class Meta:
        model = ClassLevel
        fields = ['name', 'order']


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'description']


class ClassSectionForm(forms.ModelForm):
    class Meta:
        model = ClassSection
        fields = ['class_level', 'section_name', 'class_teacher', 'academic_year']

    def __init__(self, school=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if school:
            self.fields['class_teacher'].queryset = SchoolUser.objects.filter(
                school=school, role='teacher', is_active=True
            )
            self.fields['class_level'].queryset = ClassLevel.objects.filter(school=school)
            self.fields['academic_year'].queryset = AcademicYear.objects.filter(school=school)


class StudentForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()

    class Meta:
        model = Student
        fields = [
            'admission_number', 'date_of_birth', 'gender', 'address', 'phone',
            'current_class', 'parent_name', 'parent_phone', 'parent_email', 'photo'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, school=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if school:
            self.fields['current_class'].queryset = ClassSection.objects.filter(school=school)


class TeacherAssignmentForm(forms.ModelForm):
    class Meta:
        model = TeacherSubjectAssignment
        fields = ['teacher', 'subject', 'class_section', 'academic_year']

    def __init__(self, school=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if school:
            self.fields['teacher'].queryset = SchoolUser.objects.filter(
                school=school, role='teacher', is_active=True
            )
            self.fields['subject'].queryset = Subject.objects.filter(school=school)
            self.fields['class_section'].queryset = ClassSection.objects.filter(school=school)
            self.fields['academic_year'].queryset = AcademicYear.objects.filter(school=school)
