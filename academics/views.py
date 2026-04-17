"""
Academics views - Classes, subjects, students management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User

from .models import AcademicYear, ClassLevel, Subject, ClassSection, Student, TeacherSubjectAssignment
from .forms import AcademicYearForm, ClassLevelForm, SubjectForm, ClassSectionForm, StudentForm, TeacherAssignmentForm
from schools.models import SchoolUser


# Academic Year Views
@method_decorator(login_required, name='dispatch')
class AcademicYearListView(ListView):
    model = AcademicYear
    template_name = 'academics/academic_year_list.html'
    context_object_name = 'academic_years'

    def get_queryset(self):
        return AcademicYear.objects.filter(school=self.request.school)


@method_decorator(login_required, name='dispatch')
class AcademicYearCreateView(CreateView):
    model = AcademicYear
    form_class = AcademicYearForm
    template_name = 'academics/academic_year_form.html'
    success_url = reverse_lazy('academics:academic_year_list')

    def form_valid(self, form):
        form.instance.school = self.request.school
        messages.success(self.request, 'Academic year created successfully!')
        return super().form_valid(form)


# Class Level Views
@method_decorator(login_required, name='dispatch')
class ClassLevelListView(ListView):
    model = ClassLevel
    template_name = 'academics/class_level_list.html'
    context_object_name = 'class_levels'

    def get_queryset(self):
        return ClassLevel.objects.filter(school=self.request.school)


@method_decorator(login_required, name='dispatch')
class ClassLevelCreateView(CreateView):
    model = ClassLevel
    form_class = ClassLevelForm
    template_name = 'academics/class_level_form.html'
    success_url = reverse_lazy('academics:class_level_list')

    def form_valid(self, form):
        form.instance.school = self.request.school
        messages.success(self.request, 'Class level created successfully!')
        return super().form_valid(form)


# Subject Views
@method_decorator(login_required, name='dispatch')
class SubjectListView(ListView):
    model = Subject
    template_name = 'academics/subject_list.html'
    context_object_name = 'subjects'

    def get_queryset(self):
        return Subject.objects.filter(school=self.request.school)


@method_decorator(login_required, name='dispatch')
class SubjectCreateView(CreateView):
    model = Subject
    form_class = SubjectForm
    template_name = 'academics/subject_form.html'
    success_url = reverse_lazy('academics:subject_list')

    def form_valid(self, form):
        form.instance.school = self.request.school
        messages.success(self.request, 'Subject created successfully!')
        return super().form_valid(form)


# Class Section Views
@method_decorator(login_required, name='dispatch')
class ClassSectionListView(ListView):
    model = ClassSection
    template_name = 'academics/class_section_list.html'
    context_object_name = 'class_sections'

    def get_queryset(self):
        return ClassSection.objects.filter(school=self.request.school).select_related('class_level', 'academic_year')


@method_decorator(login_required, name='dispatch')
class ClassSectionCreateView(CreateView):
    model = ClassSection
    form_class = ClassSectionForm
    template_name = 'academics/class_section_form.html'
    success_url = reverse_lazy('academics:class_section_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = self.request.school
        return kwargs

    def form_valid(self, form):
        form.instance.school = self.request.school
        messages.success(self.request, 'Class section created successfully!')
        return super().form_valid(form)


# Student Views
@method_decorator(login_required, name='dispatch')
class StudentListView(ListView):
    model = Student
    template_name = 'academics/student_list.html'
    context_object_name = 'students'
    paginate_by = 20

    def get_queryset(self):
        queryset = Student.objects.filter(school=self.request.school).select_related('user', 'current_class')

        # Filter by class if provided
        class_id = self.request.GET.get('class')
        if class_id:
            queryset = queryset.filter(current_class_id=class_id)

        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                user__first_name__icontains=search
            ) | queryset.filter(
                user__last_name__icontains=search
            ) | queryset.filter(
                admission_number__icontains=search
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['class_sections'] = ClassSection.objects.filter(school=self.request.school)
        return context


@method_decorator(login_required, name='dispatch')
class StudentCreateView(CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'academics/student_form.html'
    success_url = reverse_lazy('academics:student_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = self.request.school
        return kwargs

    def form_valid(self, form):
        # Create user for student
        user = User.objects.create_user(
            username=form.cleaned_data['email'],
            email=form.cleaned_data['email'],
            password=User.objects.make_random_password(),
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name']
        )

        # Create SchoolUser link
        school_user = SchoolUser.objects.create(
            user=user,
            school=self.request.school,
            role='student',
            is_active=True
        )

        form.instance.user = user
        form.instance.school = self.request.school
        form.instance.school_user = school_user

        messages.success(self.request, f'Student {user.get_full_name()} created successfully!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class StudentDetailView(DetailView):
    model = Student
    template_name = 'academics/student_detail.html'
    context_object_name = 'student'

    def get_queryset(self):
        return Student.objects.filter(school=self.request.school)


# Teacher Assignment Views
@method_decorator(login_required, name='dispatch')
class TeacherAssignmentListView(ListView):
    model = TeacherSubjectAssignment
    template_name = 'academics/teacher_assignment_list.html'
    context_object_name = 'assignments'

    def get_queryset(self):
        return TeacherSubjectAssignment.objects.filter(
            class_section__school=self.request.school
        ).select_related('teacher', 'subject', 'class_section')


@method_decorator(login_required, name='dispatch')
class TeacherAssignmentCreateView(CreateView):
    model = TeacherSubjectAssignment
    form_class = TeacherAssignmentForm
    template_name = 'academics/teacher_assignment_form.html'
    success_url = reverse_lazy('academics:teacher_assignment_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = self.request.school
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Teacher assigned successfully!')
        return super().form_valid(form)
