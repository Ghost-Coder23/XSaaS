"""
Reports models - PDF generation and report card templates
"""
from django.db import models
from results.models import TermSummary, YearlyResult


class ReportCardTemplate(models.Model):
    """Customizable report card template for a school"""
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='report_templates')
    name = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)

    # Header configuration
    show_logo = models.BooleanField(default=True)
    show_school_name = models.BooleanField(default=True)
    show_motto = models.BooleanField(default=True)
    show_address = models.BooleanField(default=True)

    # Content configuration
    show_attendance = models.BooleanField(default=True)
    show_class_position = models.BooleanField(default=True)
    show_teacher_comments = models.BooleanField(default=True)
    show_headmaster_comment = models.BooleanField(default=True)

    # Signature configuration
    headmaster_signature = models.ImageField(upload_to='signatures/', blank=True, null=True)
    headmaster_name = models.CharField(max_length=200, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.school.name}"


class GeneratedReport(models.Model):
    """Track generated PDF reports"""
    REPORT_TYPE_CHOICES = [
        ('term', 'Term Report'),
        ('yearly', 'Yearly Report'),
        ('transcript', 'Transcript'),
    ]

    term_summary = models.ForeignKey(TermSummary, on_delete=models.CASCADE, null=True, blank=True)
    yearly_result = models.ForeignKey(YearlyResult, on_delete=models.CASCADE, null=True, blank=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)

    pdf_file = models.FileField(upload_to='reports/%Y/%m/')
    generated_by = models.ForeignKey('schools.SchoolUser', on_delete=models.SET_NULL, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    download_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.report_type} - {self.generated_at}"
