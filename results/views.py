"""
Results views - Marks entry, approval, and management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.db import transaction

from core.utils import SchoolRoleMixin, school_role_required
from .models import Term, GradeScale, StudentResult, TermSummary
from .forms import TermForm, GradeScaleForm, StudentResultForm, BulkResultEntryForm, TermApprovalForm
from academics.models import Student, Subject, ClassSection, AcademicYear


@method_decorator(login_required, name='dispatch')
class TermListView(ListView):
    model = Term
    template_name = 'results/term_list.html'
    context_object_name = 'terms'

    def get_queryset(self):
        return Term.objects.filter(
            academic_year__school=self.request.school
        ).select_related('academic_year')


@method_decorator(login_required, name='dispatch')
class TermCreateView(CreateView):
    model = Term
    form_class = TermForm
    template_name = 'results/term_form.html'
    success_url = reverse_lazy('results:term_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if hasattr(form, 'fields') and 'academic_year' in form.fields:
            form.fields['academic_year'].queryset = AcademicYear.objects.filter(school=self.request.school)
        return form

    def form_valid(self, form):
        messages.success(self.request, 'Term created successfully!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class GradeScaleListView(ListView):
    model = GradeScale
    template_name = 'results/grade_scale_list.html'
    context_object_name = 'grade_scales'

    def get_queryset(self):
        return GradeScale.objects.filter(school=self.request.school)


@method_decorator(login_required, name='dispatch')
class GradeScaleCreateView(CreateView):
    model = GradeScale
    form_class = GradeScaleForm
    template_name = 'results/grade_scale_form.html'
    success_url = reverse_lazy('results:grade_scale_list')

    def form_valid(self, form):
        form.instance.school = self.request.school
        messages.success(self.request, 'Grade scale added successfully!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class GradeScaleUpdateView(UpdateView):
    model = GradeScale
    form_class = GradeScaleForm
    template_name = 'results/grade_scale_form.html'
    success_url = reverse_lazy('results:grade_scale_list')

    def get_queryset(self):
        return GradeScale.objects.filter(school=self.request.school)

    def form_valid(self, form):
        messages.success(self.request, 'Grade scale updated successfully!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class GradeScaleDeleteView(DeleteView):
    model = GradeScale
    template_name = 'results/grade_scale_confirm_delete.html'
    success_url = reverse_lazy('results:grade_scale_list')

    def get_queryset(self):
        return GradeScale.objects.filter(school=self.request.school)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Grade scale deleted successfully!')
        return super().delete(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class ResultEntryView(TemplateView):
    template_name = 'results/result_entry.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        school = self.request.school

        class_section_id = self.request.GET.get('class')
        subject_id = self.request.GET.get('subject')
        term_id = self.request.GET.get('term')

        if class_section_id and subject_id and term_id:
            class_section = get_object_or_404(ClassSection, id=class_section_id, school=school)
            subject = get_object_or_404(Subject, id=subject_id, school=school)
            term = get_object_or_404(Term, id=term_id, academic_year__school=school)

            students = Student.objects.filter(
                current_class=class_section,
                school=school,
                is_active=True
            )

            school_user = self.request.user.school_memberships.filter(school=school).first()

            results = []
            for student in students:
                result, created = StudentResult.objects.get_or_create(
                    student=student,
                    subject=subject,
                    term=term,
                    defaults={
                        'class_section': class_section,
                        'entered_by': school_user,
                        'status': 'draft'
                    }
                )
                results.append(result)

            context['class_section'] = class_section
            context['subject'] = subject
            context['term'] = term
            context['results'] = results

        context['classes'] = ClassSection.objects.filter(school=school)
        context['subjects'] = Subject.objects.filter(school=school)
        context['terms'] = Term.objects.filter(academic_year__school=school)
        return context

    def post(self, request, *args, **kwargs):
        school = request.school
        school_user = request.user.school_memberships.filter(school=school).first()

        with transaction.atomic():
            for key, value in request.POST.items():
                if key.startswith('ca_'):
                    result_id = key.replace('ca_', '')
                    try:
                        result = StudentResult.objects.get(
                            id=result_id,
                            class_section__school=school
                        )
                        if result.status == 'locked':
                            continue
                        result.continuous_assessment = float(value or 0)
                        result.exam_score = float(request.POST.get(f'exam_{result_id}', 0) or 0)
                        result.teacher_comment = request.POST.get(f'comment_{result_id}', '')
                        result.entered_by = school_user
                        result.calculate_total()

                        grade_scales = GradeScale.objects.filter(school=school).order_by('-min_score')
                        result.assign_grade(grade_scales)

                        result.status = 'submitted'
                        result.save()
                    except (StudentResult.DoesNotExist, ValueError):
                        continue

        # Auto-calculate positions per subject
        class_id = request.POST.get('class')
        subject_id = request.POST.get('subject')
        term_id = request.POST.get('term')
        if class_id and subject_id and term_id:
            sub_results = StudentResult.objects.filter(
                class_section_id=class_id,
                subject_id=subject_id,
                term_id=term_id,
                status='submitted'
            ).order_by('-total_score')
            for i, r in enumerate(sub_results, 1):
                r.position = i
                r.save(update_fields=['position'])

        messages.success(request, 'Results submitted! Pending headmaster approval.')
        return redirect(f"{request.path}?class={class_id}&subject={subject_id}&term={term_id}")


@method_decorator(login_required, name='dispatch')
class PendingApprovalsView(ListView):
    model = StudentResult
    template_name = 'results/pending_approvals.html'
    context_object_name = 'pending_results'

    def get_queryset(self):
        return StudentResult.objects.filter(
            class_section__school=self.request.school,
            status='submitted'
        ).select_related('student__user', 'subject', 'term')

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        result_ids = request.POST.getlist('result_ids')

        results = StudentResult.objects.filter(
            id__in=result_ids,
            class_section__school=request.school
        )

        if action == 'approve':
            results.update(status='approved', approved_by=request.user.school_memberships.filter(school=request.school).first())
            messages.success(request, f'{results.count()} results approved!')
        elif action == 'lock':
            results.update(status='locked')
            messages.success(request, f'{results.count()} results locked!')

        return redirect('results:pending_approvals')


@method_decorator(login_required, name='dispatch')
class StudentResultsView(DetailView):
    model = Student
    template_name = 'results/student_results.html'
    context_object_name = 'student'

    def get_queryset(self):
        return Student.objects.filter(school=self.request.school)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.object

        context['term_summaries'] = TermSummary.objects.filter(
            student=student
        ).select_related('term', 'term__academic_year').order_by('term__academic_year', 'term__term_number')

        current_term = Term.objects.filter(
            academic_year__school=self.request.school,
            is_current=True
        ).first()

        if current_term:
            context['current_results'] = StudentResult.objects.filter(
                student=student,
                term=current_term,
                status__in=['approved', 'locked']
            ).select_related('subject')
            context['current_term'] = current_term

        return context


@login_required
@school_role_required(['headmaster'])
def approve_all_results(request):
    if request.method == 'POST':
        term_id = request.POST.get('term_id')
        school = request.school
        school_user = request.user.school_memberships.filter(school=school).first()

        qs = StudentResult.objects.filter(
            class_section__school=school,
            status='submitted'
        )
        if term_id:
            qs = qs.filter(term_id=term_id)

        count = qs.update(status='approved', approved_by=school_user)
        messages.success(request, f'{count} results approved successfully!')

    return redirect('results:pending_approvals')
