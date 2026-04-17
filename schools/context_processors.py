"""Context processors for school-wide template variables"""
from schools.models import SchoolUser


def school_context(request):
    """Add school and user role to every template context"""
    school = getattr(request, 'school', None)
    school_role = ''
    if school and request.user.is_authenticated:
        try:
            su = SchoolUser.objects.get(user=request.user, school=school, is_active=True)
            school_role = su.role
        except SchoolUser.DoesNotExist:
            pass
    return {
        'current_school': school,
        'school_role': school_role,
    }
