"""
Attendance models - Daily attendance tracking
"""
from django.db import models
from django.utils import timezone
from academics.models import Student, ClassSection
from schools.models import School, SchoolUser
from core.models import TenantManager


class AttendanceSession(models.Model):
    """A single attendance-taking session for a class on a given date"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='attendance_sessions')
    class_section = models.ForeignKey(ClassSection, on_delete=models.CASCADE, related_name='attendance_sessions')
    date = models.DateField(default=timezone.now)
    marked_by = models.ForeignKey(SchoolUser, on_delete=models.SET_NULL, null=True, related_name='attendance_sessions')
    is_finalized = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TenantManager()
    all_objects = models.Manager()

    class Meta:
        unique_together = ['class_section', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.class_section} - {self.date}"

    def get_summary(self):
        records = self.records.all()
        total = records.count()
        present = records.filter(status='present').count()
        absent = records.filter(status='absent').count()
        late = records.filter(status='late').count()
        excused = records.filter(status='excused').count()
        pct = round((present / total) * 100, 1) if total > 0 else 0
        return {
            'total': total, 'present': present, 'absent': absent,
            'late': late, 'excused': excused, 'percentage': pct,
        }


class AttendanceRecord(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]

    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='records')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    notes = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ['session', 'student']
        ordering = ['student__user__last_name']

    def __str__(self):
        return f"{self.student} - {self.session.date} - {self.status}"
