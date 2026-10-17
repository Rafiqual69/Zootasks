from functools import wraps

from django.conf import settings
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.utils import timezone

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

    An Owner who has not recently completed the password/TOTP step must restart
    Owner login. A recently reauthenticated Owner can complete passkey binding
    in the verification center. Non-Owner staff accounts retain their normal
    authentication/authorization path.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    @staticmethod
    def _has_recent_owner_reauthentication(request):
        timestamp = request.session.get("owner_reauthenticated_at")
        if timestamp is None:
            return False
        try:
            age = timezone.now().timestamp() - float(timestamp)
        except (TypeError, ValueError):
            return False
        return 0 <= age <= settings.OWNER_WEBAUTHN_REAUTH_TTL_SECONDS

    def __call__(self, request):
        is_admin_path = (
            request.path_info == "/admin"
            or request.path_info.startswith("/admin/")
        )
        if (
            is_admin_path
            and getattr(request.user, "is_authenticated", False)
            and is_owner(request.user)
            and not is_owner_session_bound(request)
        ):
            destination = (
                "owner_verification_center"
                if self._has_recent_owner_reauthentication(request)
                else "owner_login"
            )
            response = redirect(destination)
            response["Cache-Control"] = "no-store"
            response["Referrer-Policy"] = "no-referrer"
            return response

        return self.get_response(request)
