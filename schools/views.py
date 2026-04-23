"""
Schools views - Public website and school management
"""
from datetime import date

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView, ListView, UpdateView
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django import forms
from django.db import transaction
from django.db.models import Sum
from django.utils.decorators import method_decorator
from django.core.mail import send_mail

from .models import School, SchoolUser
from .forms import SchoolRegistrationForm, SchoolBrandingForm, AddSchoolUserForm, ParentRegistrationForm, SchoolUserEditForm


class HomeView(TemplateView):
    #Landing page for schools where theye register their schools and get the credential for their space
    template_name = 'schools/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_schools_count'] = School.objects.filter(status='active').count()
        context['features'] = [
            {
                'icon': 'bi-clipboard-data',
                'title': 'Smart Results Management',
                'description': 'Effortlessly manage term results with automated calculations and grading.'
            },
            {
                'icon': 'bi-people',
                'title': 'Parent & Student Portal',
                'description': 'Give parents and students instant access to results and progress reports.'
            },
            {
                'icon': 'bi-building',
                'title': 'Multi-Tenant Architecture',
                'description': 'Each school gets their own private subdomain with complete data isolation.'
            },
            {
                'icon': 'bi-file-pdf',
                'title': 'PDF Report Cards',
                'description': 'Generate professional report cards with your school branding.'
            },
            {
                'icon': 'bi-shield-check',
                'title': 'Role-Based Access',
                'description': 'Secure access control for headmasters, admins, teachers, students, and parents.'
            },
            {
                'icon': 'bi-graph-up',
                'title': 'Analytics Dashboard',
                'description': 'Track performance trends and generate insights for better decision making.'
            },
        ]
        return context


class FeaturesView(TemplateView):
    """Features page"""
    template_name = 'schools/features.html'


class PricingView(TemplateView):
    """Pricing page"""
    template_name = 'schools/pricing.html'


class ContactView(TemplateView):
    """Contact page"""
    template_name = 'schools/contact.html'


class SchoolRegistrationView(CreateView):
    """School self-registration view"""
    model = School
    form_class = SchoolRegistrationForm
    template_name = 'schools/register_school.html'
    success_url = reverse_lazy('registration_pending')

    def form_valid(self, form):
        try:
            with transaction.atomic():
                # Create school
                school = form.save(commit=False)
                school.status = 'pending'
                school.save()

                # Create headmaster user
                user = User.objects.create_user(
                    username=form.cleaned_data['headmaster_email'],
                    email=form.cleaned_data['headmaster_email'],
                    password=form.cleaned_data['headmaster_password'],
                    first_name=form.cleaned_data['headmaster_first_name'],
                    last_name=form.cleaned_data['headmaster_last_name']
                )

                # Create SchoolUser link
                SchoolUser.objects.create(
                    user=user,
                    school=school,
                    role='headmaster',
                    is_active=True
                )

                # Send notification to platform owner
                self.notify_platform_owner(school)

                messages.success(
                    self.request, 
                    f'Registration successful! Your school "{school.name}" is pending approval. '
                    f'You will be notified at {school.email} once approved.'
                )

                return redirect('home')

        except Exception as e:
            messages.error(self.request, f'Registration failed: {str(e)}')
            return self.form_invalid(form)

    def notify_platform_owner(self, school):
        """Send email notification to platform owner"""
        try:
            send_mail(
                subject=f'New School Registration: {school.name}',
                message=f'A new school "{school.name}" has registered and is pending approval.\n'
                        f'Subdomain: {school.subdomain}\n'
                        f'Email: {school.email}',
                from_email='noreply@educore.com',
                recipient_list=['admin@educore.com'],
                fail_silently=True
            )
        except:
            pass


# School Admin Views (require login and school membership)
@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    """Legacy dashboard endpoint; forwards to unified analytics dashboard"""
    template_name = 'schools/dashboard.html'

    def get(self, request, *_, **__):
        # Single source of truth for role-based dashboards lives in analytics.views.dashboard
        return redirect('analytics:dashboard')

    def render_headmaster_dashboard(self, request, school):
        from results.models import TermSummary, StudentResult
        from academics.models import Student, ClassSection

        context = {
            'school': school,
            'total_students': Student.objects.filter(school=school, is_active=True).count(),
            'total_teachers': SchoolUser.objects.filter(school=school, role='teacher').count(),
            'total_classes': ClassSection.objects.filter(school=school).count(),
            'pending_approvals': StudentResult.objects.filter(
                class_section__school=school,
                status='submitted'
            ).count(),
            'recent_results': TermSummary.objects.filter(
                class_section__school=school
            ).select_related('student', 'term')[:10]
        }
        return render(request, 'schools/dashboard_headmaster.html', context)

    def render_admin_dashboard(self, request, school):
        from academics.models import Student, ClassSection
        from attendance.models import AttendanceSession
        from fees.models import FeeInvoice

        today = date.today()
        total_students = Student.objects.filter(school=school, is_active=True).count()
        total_teachers = SchoolUser.objects.filter(
            school=school, role='teacher', is_active=True
        ).count()
        total_classes = ClassSection.objects.filter(school=school).count()
        total_parents = SchoolUser.objects.filter(
            school=school, role='parent', is_active=True
        ).count()
        total_users = SchoolUser.objects.filter(school=school, is_active=True).count()

        total_invoiced = FeeInvoice.objects.filter(school=school).aggregate(
            total=Sum('amount')
        )['total'] or 0
        total_collected = FeeInvoice.objects.filter(school=school).aggregate(
            total=Sum('amount_paid')
        )['total'] or 0
        outstanding_balance = total_invoiced - total_collected
        overdue_invoices = FeeInvoice.objects.filter(
            school=school,
            status__in=['unpaid', 'partial', 'overdue'],
            due_date__lt=today
        ).count()

        classes_marked_today = AttendanceSession.objects.filter(
            school=school, date=today, is_finalized=True
        ).count()
        attendance_completion_pct = round(
            (classes_marked_today / total_classes) * 100, 1
        ) if total_classes else 0
        student_teacher_ratio = round(
            total_students / total_teachers, 1
        ) if total_teachers else None

        context = {
            'school': school,
            'today': today,
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_classes': total_classes,
            'total_parents': total_parents,
            'total_users': total_users,
            'total_invoiced': total_invoiced,
            'total_collected': total_collected,
            'outstanding_balance': outstanding_balance,
            'overdue_invoices': overdue_invoices,
            'classes_marked_today': classes_marked_today,
            'attendance_completion_pct': attendance_completion_pct,
            'student_teacher_ratio': student_teacher_ratio,
        }
        return render(request, 'schools/dashboard_admin.html', context)

    def render_teacher_dashboard(self, request, school):
        from academics.models import TeacherSubjectAssignment

        assignments = TeacherSubjectAssignment.objects.filter(
            teacher__user=request.user,
            class_section__school=school
        ).select_related('subject', 'class_section')

        context = {
            'school': school,
            'assignments': assignments,
        }
        return render(request, 'schools/dashboard_teacher.html', context)

    def render_student_dashboard(self, request, school):
        from results.models import TermSummary
        from academics.models import Student

        try:
            student = Student.objects.get(user=request.user, school=school)
            summaries = TermSummary.objects.filter(student=student).select_related('term')

            context = {
                'school': school,
                'student': student,
                'summaries': summaries,
            }
            return render(request, 'schools/dashboard_student.html', context)
        except Student.DoesNotExist:
            messages.error(request, "Student profile not found.")
            return redirect('home')

    def render_parent_dashboard(self, request, school):
        from academics.models import Student

        # Find children linked to this parent's email
        children = Student.objects.filter(
            school=school,
            parent_email=request.user.email,
            is_active=True
        )

        context = {
            'school': school,
            'children': children,
        }
        return render(request, 'schools/dashboard_parent.html', context)


@method_decorator(login_required, name='dispatch')
class SchoolSettingsView(UpdateView):
    """School branding and settings"""
    model = School
    form_class = SchoolBrandingForm
    template_name = 'schools/school_settings.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self):
        return self.request.school

    def form_valid(self, form):
        messages.success(self.request, 'School settings updated successfully!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class UserManagementView(ListView):
    """Manage school users"""
    model = SchoolUser
    template_name = 'schools/user_management.html'
    context_object_name = 'users'

    def get_queryset(self):
        return SchoolUser.objects.filter(
            school=self.request.school
        ).select_related('user').order_by('role', 'user__last_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['school'] = self.request.school
        context['add_user_form'] = AddSchoolUserForm()
        return context


@login_required
def add_school_user(request):
    """Add a new user to the school"""
    if request.method == 'POST':
        form = AddSchoolUserForm(request.POST)
        if form.is_valid():
            school = request.school

            # Create user
            import random
            import string
            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            user = User.objects.create_user(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                password=temp_password,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )

            # Create SchoolUser
            SchoolUser.objects.create(
                user=user,
                school=school,
                role=form.cleaned_data['role'],
                is_active=True
            )

            # Send welcome email with password reset link
            from django.contrib.sites.shortcuts import get_current_site
            from django.utils.http import urlsafe_base64_encode
            from django.utils.encoding import force_bytes
            from django.template.loader import render_to_string
            from django.contrib.auth.tokens import default_token_generator
            
            current_site = get_current_site(request)
            subject = 'Welcome to EduCore! Set your password'
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = f"http://{current_site.domain}/accounts/password/reset/confirm/{uid}/{token}/"
            message = render_to_string('accounts/welcome_email.txt', {
                'user': user,
                'school': school,
                'reset_link': reset_link,
            })
            user.email_user(subject, message)

            messages.success(request, f"User {user.get_full_name()} added successfully!")
            return redirect('user_management')

    return redirect('user_management')


@login_required
def school_user_edit(request, pk):
    """Edit school user details"""
    school_user = get_object_or_404(SchoolUser, pk=pk, school=request.school)
    
    class UserForm(forms.Form):
        first_name = forms.CharField()
        last_name = forms.CharField()
        email = forms.EmailField()
    
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        school_user_form = SchoolUserEditForm(request.POST, instance=school_user)
        
        if user_form.is_valid() and school_user_form.is_valid():
            # Update user
            school_user.user.first_name = user_form.cleaned_data['first_name']
            school_user.user.last_name = user_form.cleaned_data['last_name']
            school_user.user.email = user_form.cleaned_data['email']
            school_user.user.save()
            
            school_user_form.save()
            messages.success(request, f'User {school_user.user.get_full_name()} updated successfully!')
            return redirect('user_management')
    else:
        user_form = UserForm(initial={
            'first_name': school_user.user.first_name,
            'last_name': school_user.user.last_name,
            'email': school_user.user.email,
        })
        school_user_form = SchoolUserEditForm(instance=school_user)
    
    context = {
        'school_user': school_user,
        'user_form': user_form,
        'school_user_form': school_user_form,
        'school': request.school,
    }
    return render(request, 'schools/user_edit.html', context)


@login_required
def school_user_deactivate(request, pk):
    """Toggle school user active status"""
    school_user = get_object_or_404(SchoolUser, pk=pk, school=request.school)

    school_user.is_active = not school_user.is_active
    action = 'deactivated' if not school_user.is_active else 'reactivated'
    school_user.save()
    messages.success(request, f"User {school_user.user.get_full_name()} {action} successfully!")
    return redirect('user_management')



class ParentRegistrationView(CreateView):
    """Parent self-registration view"""
    form_class = ParentRegistrationForm
    template_name = 'schools/parent_register.html'
    success_url = reverse_lazy('home')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'instance' in kwargs:
            kwargs.pop('instance')
        kwargs['school'] = getattr(self.request, 'school', None)
        return kwargs



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['school'] = self.request.school
        return context

    def form_valid(self, form):
        school = self.request.school
        from academics.models import Student
        Student.objects.get(school=school, admission_number=form.cleaned_data['student_admission'])

        # Create user
        user = User.objects.create_user(
            username=form.cleaned_data['parent_email'],
            email=form.cleaned_data['parent_email'],
            password=form.cleaned_data['password1'],
            first_name=form.cleaned_data['parent_first_name'],
            last_name=form.cleaned_data['parent_last_name']
        )

        # Create SchoolUser
        SchoolUser.objects.create(
            user=user,
            school=school,
            role='parent',
            is_active=True
        )

        # Optional: update student.parent_phone if provided
        # student.parent_phone = form.cleaned_data.get('parent_phone')

        messages.success(
            self.request,
            f'Welcome {user.get_full_name()}! You can now access your child\'s results.'
        )
        # Auto-login the new parent
        user = authenticate(self.request, username=user.username, password=form.cleaned_data['password1'])
        if user:
            login(self.request, user)
        return redirect('/school/dashboard/')


from django.http import JsonResponse, HttpResponse
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET


@require_GET
@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def service_worker(_):
    """Serve the PWA service worker from templates so Django can process it"""
    import os
    sw_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'pwa', 'sw.js')
    if os.path.exists(sw_path):
        with open(sw_path, 'r') as f:
            content = f.read()
    else:
        content = "// Service Worker placeholder"
    return HttpResponse(content, content_type='application/javascript')


def pwa_manifest(request):
    """Dynamic PWA manifest with school branding"""
    school = getattr(request, 'school', None)
    name = school.name if school else 'EduCore'
    color = school.theme_color if school else '#4F46E5'
    manifest = {
        "name": name,
        "short_name": name[:12],
        "description": f"{name} School Management",
        "start_url": "/analytics/dashboard/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": color,
        "orientation": "any",
        "scope": "/",
        "icons": [
            {"src": "/static/icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/static/icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "/static/icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
        "categories": ["education", "productivity"],
        "shortcuts": [
            {"name": "Dashboard", "url": "/analytics/dashboard/", "description": "Go to dashboard"},
            {"name": "Attendance", "url": "/attendance/", "description": "Mark attendance"},
            {"name": "Students", "url": "/academics/students/", "description": "View students"},
        ]
    }
    return JsonResponse(manifest)
