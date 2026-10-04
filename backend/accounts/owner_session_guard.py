from functools import wraps

from django.http import HttpResponseForbidden

from .owner_session_binding import is_owner_session_bound


def owner_session_binding_required(view_func):
    """Fail closed unless the request has a valid server-side Owner binding."""

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not is_owner_session_bound(request):
            return HttpResponseForbidden("Owner session binding required.")
        return view_func(request, *args, **kwargs)

    return wrapper
