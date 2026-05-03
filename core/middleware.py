import threading
import time
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.conf import settings

_thread_locals = threading.local()

def set_current_school(school):
    _thread_locals.school = school

def get_current_school():
    return getattr(_thread_locals, 'school', None)

def set_current_user(user):
    _thread_locals.user = user

def get_current_user():
    return getattr(_thread_locals, 'user', None)


class RateLimitMiddleware:
    """
    Middleware to enforce rate limiting at multiple levels:
    - Per IP address
    - Per User (if logged in)
    - Per School (tenant wide)
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Thresholds (requests per minute)
        self.IP_LIMIT = 100
        self.USER_LIMIT = 200
        self.SCHOOL_LIMIT = 1000

    def __call__(self, request):
        if settings.DEBUG:
            return self.get_response(request)

        # 1. IP Based Limit
        ip = self.get_client_ip(request)
        if not self.is_allowed(f"ratelimit_ip_{ip}", self.IP_LIMIT):
            return HttpResponseForbidden("IP rate limit exceeded. Please try again in a minute.")

        # 2. User Based Limit
        if request.user.is_authenticated:
            user_id = request.user.id
            if not self.is_allowed(f"ratelimit_user_{user_id}", self.USER_LIMIT):
                return HttpResponseForbidden("User rate limit exceeded. Please try again in a minute.")

        # 3. School Based Limit
        school = getattr(request, 'school', None)
        if school:
            if not self.is_allowed(f"ratelimit_school_{school.id}", self.SCHOOL_LIMIT):
                return HttpResponseForbidden("School workspace is under heavy load. Please try again in a minute.")

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def is_allowed(self, key, limit):
        """Checks if the request is allowed based on the key and limit."""
        # We use a 60-second window
        current_minute = int(time.time() / 60)
        cache_key = f"{key}_{current_minute}"
        
        try:
            count = cache.get(cache_key, 0)
            if count >= limit:
                return False
            
            # Increment and set expiry to 61s to ensure it covers the minute window
            cache.set(cache_key, count + 1, 61)
            return True
        except Exception:
            # Fallback to allow if cache fails (e.g. Redis down)
            return True


class CoreContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_current_school(getattr(request, 'school', None))
        set_current_user(getattr(request, 'user', None))
        
        response = self.get_response(request)
        
        # Cleanup
        set_current_school(None)
        set_current_user(None)
        
        return response
