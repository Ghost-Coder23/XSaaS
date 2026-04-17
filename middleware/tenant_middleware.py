"""
School Tenant Middleware - Handles subdomain-based tenant detection
Supports subdomain routing for production and ?school= param for local dev.
"""
from schools.models import School


class SchoolMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0]  # strip port
        school = None

        # 1. Subdomain routing (production: school.educore.com)
        parts = host.split('.')
        if len(parts) >= 3 and parts[-2] == 'educore' and parts[-1] == 'com':
            subdomain = parts[0]
            if subdomain not in ('www', 'admin'):
                try:
                    school = School.objects.get(subdomain=subdomain, status='active')
                except School.DoesNotExist:
                    pass

        # 2. Local dev support: ?school=subdomain or school subdomain as first part of localhost
        #    e.g. http://demo.localhost:8000
        if school is None and host.endswith('.localhost'):
            subdomain = host.replace('.localhost', '')
            try:
                school = School.objects.get(subdomain=subdomain, status='active')
            except School.DoesNotExist:
                pass

        # 3. Local dev: ?school=subdomain query param OR session-stored school
        if school is None:
            subdomain_param = request.GET.get('school') or request.session.get('school_subdomain')
            if subdomain_param:
                try:
                    school = School.objects.get(subdomain=subdomain_param, status='active')
                    request.session['school_subdomain'] = subdomain_param
                except School.DoesNotExist:
                    pass

        # 4. If user is authenticated, find their school from membership
        if school is None and hasattr(request, 'user') and request.user.is_authenticated:
            membership = request.user.school_memberships.select_related('school').filter(
                is_active=True, school__status='active'
            ).first()
            if membership:
                school = membership.school
                request.session['school_subdomain'] = school.subdomain

        request.school = school
        return self.get_response(request)
