"""
Accounts views - Authentication and user management
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView, LogoutView

from .forms import CustomAuthenticationForm, UserProfileForm, PasswordChangeForm


class CustomLoginView(LoginView):
    """Custom login view with school context awareness"""
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        school = getattr(self.request, 'school', None)
        if school:
            context['school'] = school
            context['login_title'] = f'Login to {school.name}'
        else:
            context['login_title'] = 'Login to EduCore'
        return context

    def form_valid(self, form):
        """Check if user has access to the school context"""
        response = super().form_valid(form)
        school = getattr(self.request, 'school', None)

        if school:
            from schools.models import SchoolUser
            try:
                membership = SchoolUser.objects.get(
                    user=self.request.user,
                    school=school,
                    is_active=True
                )
                messages.success(
                    self.request, 
                    f'Welcome back, {self.request.user.get_full_name() or self.request.user.username}!'
                )
            except SchoolUser.DoesNotExist:
                # User exists but doesn't belong to this school
                logout(self.request)
                messages.error(
                    self.request,
                    'You do not have access to this school. Please contact your administrator.'
                )
                return redirect('accounts:login')

        return response


class CustomLogoutView(LogoutView):
    """Custom logout view - allows GET, redirects to home"""
    http_method_names = ['get', 'post']

    def get_success_url(self):
        from django.urls import reverse
        try:
            return reverse('home')
        except:
            return '/'

    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('home')

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('home')


@login_required
def profile_view(request):
    """User profile view"""
    if request.method == 'POST':
        form = UserProfileForm(
            request.POST, 
            request.FILES, 
            instance=request.user.profile
        )
        if form.is_valid():
            # Update user fields
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()

            # Update profile
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user.profile, initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        })

    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def change_password_view(request):
    """Change password view"""
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['new_password'])
            request.user.save()
            messages.success(request, 'Password changed successfully! Please login again.')
            return redirect('accounts:login')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'accounts/change_password.html', {'form': form})
