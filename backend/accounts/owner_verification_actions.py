from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from .email_verification import issue_owner_email_verification
from .policies import is_owner


@login_required
@require_POST
def request_owner_email_verification(request):
    if not is_owner(request.user):
        return redirect("login")

    try:
        issue_owner_email_verification(request, request.user)
    except (ValidationError, ValueError) as exc:
        messages.error(request, str(exc))
    else:
        messages.success(
            request,
            "Owner email verification message has been requested. Check the configured Owner inbox.",
        )

    return redirect("owner_verification_center")
