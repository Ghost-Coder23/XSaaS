import threading

_thread_locals = threading.local()

def set_current_school(school):
    _thread_locals.school = school

def get_current_school():
    return getattr(_thread_locals, 'school', None)

def set_current_user(user):
    _thread_locals.user = user

def get_current_user():
    return getattr(_thread_locals, 'user', None)


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
