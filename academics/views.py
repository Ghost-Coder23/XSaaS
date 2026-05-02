"""
Academics views - Classes, subjects, students management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User

from .models import AcademicYear, ClassLevel, Subject, ClassSection, Student, TeacherSubjectAssignment
from .forms import AcademicYearForm, ClassLevelForm, SubjectForm, ClassSectionForm, StudentForm, TeacherForm, TeacherAssignmentForm
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


@method_decorator(login_required, name='dispatch')
class AcademicYearUpdateView(UpdateView):
    model = AcademicYear
    form_class = AcademicYearForm
    template_name = 'academics/academic_year_form.html'
    success_url = reverse_lazy('academics:academic_year_list')

    def get_queryset(self):
        return AcademicYear.objects.filter(school=self.request.school)

    def form_valid(self, form):
        messages.success(self.request, 'Academic year updated successfully!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class AcademicYearDeleteView(DeleteView):
    model = AcademicYear
    template_name = 'academics/academic_year_confirm_delete.html'
    success_url = reverse_lazy('academics:academic_year_list')

    def get_queryset(self):
        return AcademicYear.objects.filter(school=self.request.school)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Academic year deleted successfully!')
        return super().delete(request, *args, **kwargs)


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


@method_decorator(login_required, name='dispatch')
class ClassLevelUpdateView(UpdateView):
    model = ClassLevel
    form_class = ClassLevelForm
    template_name = 'academics/class_level_form.html'
    success_url = reverse_lazy('academics:class_level_list')

    def get_queryset(self):
        return ClassLevel.objects.filter(school=self.request.school)

    def form_valid(self, form):
        messages.success(self.request, 'Class level updated successfully!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class ClassLevelDeleteView(DeleteView):
    model = ClassLevel
    template_name = 'academics/class_level_confirm_delete.html'
    success_url = reverse_lazy('academics:class_level_list')

    def get_queryset(self):
        return ClassLevel.objects.filter(school=self.request.school)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Class level deleted successfully!')
        return super().delete(request, *args, **kwargs)


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
        import string
        import random
        from datetime import datetime
        from .models import Student
        password_chars = string.ascii_letters + string.digits
        password = ''.join(random.choice(password_chars) for _ in range(12))
        user = User.objects.create_user(
            username=form.cleaned_data['email'],
            email=form.cleaned_data['email'],
            password=password,
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

        # Generate admission number: YYYY###
        current_year = datetime.now().year
        last_student = Student.objects.filter(
            school=self.request.school,
            admission_number__startswith=str(current_year)
        ).order_by('-admission_number').first()
        if last_student and last_student.admission_number[4:].isdigit():
            next_seq = int(last_student.admission_number[4:]) + 1
        else:
            next_seq = 1
        admission_number = f"{current_year}{next_seq:03d}"
        form.instance.admission_number = admission_number

        form.instance.user = user
        form.instance.school = self.request.school
        form.instance.school_user = school_user

        messages.success(self.request, f'Student {user.get_full_name()} created successfully! Admission Number: {admission_number}')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class StudentDetailView(DetailView):
    model = Student
    template_name = 'academics/student_detail.html'
    context_object_name = 'student'

    def get_queryset(self):
        return Student.objects.filter(school=self.request.school)


# Teacher Views
@method_decorator(login_required, name='dispatch')
class TeacherListView(ListView):
    model = SchoolUser
    template_name = 'academics/teacher_list.html'
    context_object_name = 'teachers'
    
    def get_queryset(self):
        return SchoolUser.objects.filter(
            school=self.request.school,
            role='teacher',
            is_active=True
        ).select_related('user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assignments'] = TeacherSubjectAssignment.objects.filter(
            class_section__school=self.request.school
        ).select_related('teacher__user', 'subject', 'class_section')
        context['teachers'] = self.get_queryset()
        return context


@method_decorator(login_required, name='dispatch')
class TeacherCreateView(CreateView):
    model = SchoolUser
    form_class = TeacherForm
    template_name = 'academics/teacher_form.html'
    success_url = reverse_lazy('academics:teacher_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = self.request.school
        return kwargs

    def form_valid(self, form):
        from django.contrib.auth.models import User
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from django.contrib.sites.shortcuts import get_current_site
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        
        cleaned_data = form.cleaned_data
        
        # Create user
        password = User.objects.make_random_password()
        user = User.objects.create_user(
            username=cleaned_data['email'],
            email=cleaned_data['email'],
            first_name=cleaned_data['first_name'],
            last_name=cleaned_data['last_name'],
            password=password
        )
        
        # Create SchoolUser
        school_user = form.save(commit=False)
        school_user.user = user
        school_user.school = self.request.school
        school_user.role = 'teacher'
        school_user.is_active = True
        school_user.save()
        
        # Send welcome email with password reset
        current_site = get_current_site(self.request)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = f"https://{current_site.domain}/accounts/password/reset/confirm/{uid}/{token}/"
        
        subject = 'Welcome to EduCore! Set Your Password'
        message = render_to_string('accounts/welcome_email.txt', {
            'user': user,
            'school': self.request.school,
            'reset_link': reset_url,
        })
        send_mail(subject, message, 'noreply@educore.com', [user.email], html_message=message)
        
        # Create teacher-subject assignments
        subjects = cleaned_data.get('subjects', [])
        classes = cleaned_data.get('classes', [])
        for subject in subjects:
            for class_section in classes:
                TeacherSubjectAssignment.objects.get_or_create(
                    teacher=school_user,
                    subject=subject,
                    class_section=class_section,
                    academic_year__is_current=True,  # Current year
                    defaults={'academic_year': AcademicYear.objects.filter(school=self.request.school, is_current=True).first()}
                )
        
        messages.success(self.request, f'Teacher {user.get_full_name()} created and notified!')
        return super().form_valid(form)


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


# Student Edit/Delete Views
@method_decorator(login_required, name='dispatch')
class StudentUpdateView(UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'academics/student_form.html'
    success_url = reverse_lazy('academics:student_list')

    def get_queryset(self):
        return Student.objects.filter(school=self.request.school)

    def form_valid(self, form):
        messages.success(self.request, 'Student updated successfully!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class StudentDeleteView(DeleteView):
    model = Student
    template_name = 'academics/student_confirm_delete.html'
    success_url = reverse_lazy('academics:student_list')

    def get_queryset(self):
        return Student.objects.filter(school=self.request.school)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Student deleted successfully!')
        return super().delete(request, *args, **kwargs)


# Subject Edit/Delete Views
@method_decorator(login_required, name='dispatch')
class SubjectUpdateView(UpdateView):
    model = Subject
    form_class = SubjectForm
    template_name = 'academics/subject_form.html'
    success_url = reverse_lazy('academics:subject_list')

    def get_queryset(self):
        return Subject.objects.filter(school=self.request.school)

    def form_valid(self, form):
        messages.success(self.request, 'Subject updated successfully!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class SubjectDeleteView(DeleteView):
    model = Subject
    template_name = 'academics/subject_confirm_delete.html'
    success_url = reverse_lazy('academics:subject_list')

    def get_queryset(self):
        return Subject.objects.filter(school=self.request.school)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Subject deleted successfully!')
        return super().delete(request, *args, **kwargs)


# Class Section Edit/Delete Views
@method_decorator(login_required, name='dispatch')
class ClassSectionUpdateView(UpdateView):
    model = ClassSection
    form_class = ClassSectionForm
    template_name = 'academics/class_section_form.html'
    success_url = reverse_lazy('academics:class_section_list')

    def get_queryset(self):
        return ClassSection.objects.filter(school=self.request.school)

    def form_valid(self, form):
        messages.success(self.request, 'Class section updated successfully!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class ClassSectionDeleteView(DeleteView):
    model = ClassSection
    template_name = 'academics/class_section_confirm_delete.html'
    success_url = reverse_lazy('academics:class_section_list')

    def get_queryset(self):
        return ClassSection.objects.filter(school=self.request.school)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Class section deleted successfully!')
        return super().delete(request, *args, **kwargs)


# Teacher Edit/Delete Views
@method_decorator(login_required, name='dispatch')
class TeacherUpdateView(UpdateView):
    model = SchoolUser
    form_class = TeacherForm
    template_name = 'academics/teacher_form.html'
    success_url = reverse_lazy('academics:teacher_list')

    def get_queryset(self):
        return SchoolUser.objects.filter(school=self.request.school, role='teacher')

    def form_valid(self, form):
        messages.success(self.request, 'Teacher updated successfully!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class TeacherDeleteView(DeleteView):
    model = SchoolUser
    template_name = 'academics/teacher_confirm_delete.html'
    success_url = reverse_lazy('academics:teacher_list')

    def get_queryset(self):
        return SchoolUser.objects.filter(school=self.request.school, role='teacher')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Teacher deleted successfully!')
        return super().delete(request, *args, **kwargs)
