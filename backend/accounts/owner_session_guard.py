from functools import wraps

from django.http import HttpResponseForbidden
from django.shortcuts import redirect

from .owner_session_binding import is_owner_session_bound
from .policies import is_owner


def owner_session_binding_required(view_func):
    """Fail closed unless the request has a valid server-side Owner binding."""

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not is_owner_session_bound(request):
            return HttpResponseForbidden("Owner session binding required.")
        return view_func(request, *args, **kwargs)

    return wrapper


class OwnerAdminSessionBindingMiddleware:
    """Require a live device/passkey-bound session for canonical Owner admin access.

    Anonymous login requests and non-Owner staff accounts retain their normal
    authentication/authorization path. A logged-in canonical Owner without a
    valid binding is sent to the verification center to complete passkey auth.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            (request.path_info == "/admin" or request.path_info.startswith("/admin/"))
            and getattr(request.user, "is_authenticated", False)
            and is_owner(request.user)
            and not is_owner_session_bound(request)
        ):
            response = redirect("owner_verification_center")
            response["Cache-Control"] = "no-store"
            response["Referrer-Policy"] = "no-referrer"
            return response

        return self.get_response(request)
