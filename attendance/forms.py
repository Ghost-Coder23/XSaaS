"""Attendance forms"""
from django import forms
from .models import AttendanceSession, AttendanceRecord
from academics.models import ClassSection
from results.models import Term


class AttendanceSessionForm(forms.ModelForm):
    class Meta:
        model = AttendanceSession
        fields = ['class_section', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, school=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if school:
            self.fields['class_section'].queryset = ClassSection.objects.filter(school=school)
