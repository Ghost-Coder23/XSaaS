"""
Results models - Marks, Grades, and Report Cards
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from academics.models import Student, Subject, ClassSection, AcademicYear, TeacherSubjectAssignment
from core.models import TenantManager, SyncBaseModel


class Term(SyncBaseModel):
    """Academic term (e.g., First Term, Second Term, Third Term)"""
    TERM_CHOICES = [
        (1, 'First Term'),
        (2, 'Second Term'),
        (3, 'Third Term'),
    ]

    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='terms')
    term_number = models.IntegerField(choices=TERM_CHOICES)
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ['academic_year', 'term_number']
        unique_together = ['academic_year', 'term_number']

    def __str__(self):
        return f"{self.name} - {self.academic_year.name}"


class GradeScale(SyncBaseModel):
    """Grading scale for a school"""
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='grade_scales')
    grade = models.CharField(max_length=5)  # A, B, C, etc.
    min_score = models.FloatField()
    max_score = models.FloatField()
    description = models.CharField(max_length=50)  # Excellent, Good, etc.

    objects = TenantManager()
    all_objects = models.Manager()

    class Meta:
        ordering = ['-min_score']

    def __str__(self):
        return f"{self.grade} ({self.min_score}-{self.max_score})"


class StudentResult(SyncBaseModel):
    """Student marks for a specific subject and term"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('locked', 'Locked'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='results', db_index=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='student_results', db_index=True)
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='student_results', db_index=True)
    class_section = models.ForeignKey(ClassSection, on_delete=models.CASCADE, related_name='results', db_index=True)

    # Assessment components (customizable per school)
    continuous_assessment = models.FloatField(
        default=0, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="CA/Classwork score"
    )
    exam_score = models.FloatField(
        default=0, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Exam score"
    )

    # Calculated fields
    total_score = models.FloatField(default=0)
    grade = models.CharField(max_length=5, blank=True)
    position = models.IntegerField(null=True, blank=True)  # Position in class for this subject

    # Comments
    teacher_comment = models.TextField(blank=True)

    # Workflow
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    entered_by = models.ForeignKey(
        'schools.SchoolUser', 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='entered_results'
    )
    approved_by = models.ForeignKey(
        'schools.SchoolUser', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_results'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'subject', 'term']
        ordering = ['-total_score']

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.term}"

    def calculate_total(self):
        """Calculate total score based on school's selected grading system"""
        school = self.class_section.school
        
        if school.grading_system == 'system':
            # System Default: 30% CA, 70% Exam
            ca_weight = 0.3
            exam_weight = 0.7
        elif school.grading_system == 'custom_weights':
            # Custom CA/Exam Weights
            ca_weight = school.ca_weight / 100.0
            exam_weight = school.exam_weight / 100.0
        elif school.grading_system == 'multiple_components':
            # TODO: Implement multiple assessment components
            # For now, fall back to custom weights
            ca_weight = school.ca_weight / 100.0
            exam_weight = school.exam_weight / 100.0
        elif school.grading_system == 'subject_specific':
            # TODO: Implement subject-specific grading
            # For now, fall back to custom weights
            ca_weight = school.ca_weight / 100.0
            exam_weight = school.exam_weight / 100.0
        else:
            # Fallback to system default
            ca_weight = 0.3
            exam_weight = 0.7
        
        self.total_score = (self.continuous_assessment * ca_weight) + (self.exam_score * exam_weight)
        return self.total_score

    def assign_grade(self, grade_scales):
        """Assign grade based on total score"""
        for scale in grade_scales:
            if scale.min_score <= self.total_score <= scale.max_score:
                self.grade = scale.grade
                return self.grade
        self.grade = 'F'
        return self.grade


class TermSummary(models.Model):
    """Summary of student performance for a term"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='term_summaries')
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='summaries')
    class_section = models.ForeignKey(ClassSection, on_delete=models.CASCADE, related_name='term_summaries')

    total_marks = models.FloatField(default=0)
    average = models.FloatField(default=0)
    class_position = models.IntegerField(null=True, blank=True)
    overall_grade = models.CharField(max_length=5, blank=True)

    headmaster_comment = models.TextField(blank=True)
    attendance_days = models.IntegerField(default=0)

    is_locked = models.BooleanField(default=False)
    locked_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'term']
        ordering = ['-average']

    def __str__(self):
        return f"{self.student} - {self.term} Summary"


class YearlyResult(models.Model):
    """Aggregated yearly results from 3 terms"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='yearly_results')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='yearly_results')

    term1_average = models.FloatField(default=0)
    term2_average = models.FloatField(default=0)
    term3_average = models.FloatField(default=0)
    yearly_average = models.FloatField(default=0)

    final_position = models.IntegerField(null=True, blank=True)
    promotion_status = models.CharField(
        max_length=20, 
        choices=[
            ('promoted', 'Promoted'),
            ('repeat', 'Repeat'),
            ('probation', 'Probation'),
        ],
        blank=True
    )

    is_generated = models.BooleanField(default=False)
    generated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['student', 'academic_year']

    def __str__(self):
        return f"{self.student} - {self.academic_year.name} Yearly Result"

    def calculate_yearly_average(self):
        """Calculate average of 3 terms"""
        self.yearly_average = (self.term1_average + self.term2_average + self.term3_average) / 3
        return self.yearly_average
