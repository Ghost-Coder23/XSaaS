from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import TenantManager, SyncBaseModel
from schools.models import School


class Subject(SyncBaseModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='timetable_subjects')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    periods_per_week = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    color = models.CharField(max_length=7, default='#6366f1')  # hex color

    objects = TenantManager()
    tenant_objects = TenantManager()

    class Meta:
        ordering = ['name']
        unique_together = ['school', 'code']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Teacher(SyncBaseModel):
    DAY_CHOICES = [
        (1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'),
        (4, 'Thursday'), (5, 'Friday'),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='timetable_teachers')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    available_days = models.JSONField(default=list)  # list of ints 1-5
    max_periods_per_day = models.PositiveIntegerField(default=6)
    subjects = models.ManyToManyField(Subject, blank=True, related_name='teachers')

    objects = TenantManager()
    tenant_objects = TenantManager()

    class Meta:
        ordering = ['name']
        unique_together = ['school', 'email']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.available_days:
            self.available_days = [1, 2, 3, 4, 5]
        super().save(*args, **kwargs)


class Classroom(SyncBaseModel):
    ROOM_TYPES = [
        ('standard', 'Standard'),
        ('lab', 'Laboratory'),
        ('computer', 'Computer Room'),
        ('hall', 'Assembly Hall'),
        ('library', 'Library'),
        ('gym', 'Gymnasium'),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='timetable_classrooms')
    room_name = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField(default=30)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='standard')

    objects = TenantManager()
    tenant_objects = TenantManager()

    class Meta:
        ordering = ['room_name']

    def __str__(self):
        return f"{self.room_name} ({self.get_room_type_display()})"


class SchoolClass(SyncBaseModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='timetable_classes')
    class_name = models.CharField(max_length=100)
    grade_level = models.PositiveIntegerField()
    section = models.CharField(max_length=10)
    class_teacher = models.ForeignKey(
        Teacher, null=True, blank=True, on_delete=models.SET_NULL, related_name='homeroom_classes'
    )

    objects = TenantManager()
    tenant_objects = TenantManager()

    class Meta:
        ordering = ['grade_level', 'section']
        verbose_name_plural = 'School Classes'

    def __str__(self):
        return self.class_name


class Period(SyncBaseModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='timetable_periods')
    start_time = models.TimeField()
    end_time = models.TimeField()
    label = models.CharField(max_length=50)
    is_break = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    objects = TenantManager()
    tenant_objects = TenantManager()

    class Meta:
        ordering = ['order', 'start_time']

    def __str__(self):
        return f"{self.label} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"


class Timetable(SyncBaseModel):
    TERM_CHOICES = [
        ('term1', 'Term 1'), ('term2', 'Term 2'), ('term3', 'Term 3'),
        ('semester1', 'Semester 1'), ('semester2', 'Semester 2'),
        ('full_year', 'Full Year'),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='timetables')
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='timetables')
    academic_year = models.CharField(max_length=20)  # e.g. "2024/2025"
    term = models.CharField(max_length=20, choices=TERM_CHOICES)
    generated_by = models.CharField(max_length=50, null=True, blank=True)
    published = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    objects = TenantManager()
    tenant_objects = TenantManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.school_class} - {self.academic_year} {self.get_term_display()}"

    def entry_count(self):
        return self.entries.count()


class TimetableEntry(SyncBaseModel):
    DAY_CHOICES = [
        (1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'),
        (4, 'Thursday'), (5, 'Friday'),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='timetable_entries')
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name='entries')
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    period = models.ForeignKey(Period, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)

    objects = TenantManager()
    tenant_objects = TenantManager()

    class Meta:
        ordering = ['day_of_week', 'period__order']

    def __str__(self):
        return (
            f"{self.get_day_of_week_display()} | {self.period.label} | "
            f"{self.subject.name} - {self.teacher.name}"
        )
