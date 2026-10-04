from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .models import AccountEntity


def worker_required(view_func):
    """Require an authenticated user with an active Worker entity."""

    @login_required
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        # Role state is authoritative server-side; missing/stale entities deny.
        is_worker = AccountEntity.objects.filter(
            user=request.user,
            entity_type=AccountEntity.EntityType.WORKER,
            is_active=True,
        ).exists()

        if not is_worker:
            raise PermissionDenied

        return view_func(request, *args, **kwargs)

    return wrapped
