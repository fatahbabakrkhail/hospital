import threading

# Create a thread-local storage object
_thread_local = threading.local()

class CurrentUserMiddleware:
    """Middleware to store the current request user in thread-local storage."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Store the authenticated user in thread-local storage
        _thread_local.user = request.user if request.user.is_authenticated else None
        return self.get_response(request)

def get_current_user():
    """Returns the current user from thread-local storage."""
    return getattr(_thread_local, "user", None)