"""MFA-gated Owner request console. Requests are queued, never executed here."""
from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from .models import OwnerInputRequest
from .owner_input_forms import OwnerInputRequestForm

OWNER_REAUTH_MAX_AGE = timedelta(minutes=15)
OWNER_REQUESTS_PER_HOUR = 10


def _owner_console_authorized(request) -> bool:
    """Require configured Owner identity, staff authority, verified OTP and fresh auth."""
    user = getattr(request, "user", None)
    configured_owner = getattr(settings, "OWNER_USERNAME", "")
    if (
        not user
        or not user.is_authenticated
        or not isinstance(configured_owner, str)
        or not configured_owner.strip()
        or user.username.casefold() != configured_owner.strip().casefold()
        or not user.is_staff
        or not user.is_superuser
    ):
        return False

    is_verified = getattr(user, "is_verified", None)
    if not callable(is_verified) or not is_verified():
        return False

    timestamp = parse_datetime(request.session.get("owner_reauthenticated_at", ""))
    if timestamp is None or timezone.is_naive(timestamp):
        return False
    age = timezone.now() - timestamp
    return timedelta(0) <= age <= OWNER_REAUTH_MAX_AGE


@login_required(login_url="owner_login")
@never_cache
@require_http_methods(["GET", "POST"])
def owner_console(request):
    """Accept private Owner requests with bounded input and fail-closed access."""
    if not _owner_console_authorized(request):
        raise PermissionDenied("Owner console access denied.")

    form = OwnerInputRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        now = timezone.now()
        with transaction.atomic():
            # Serialize rate-limit checks per Owner on databases supporting row locks.
            owner = get_user_model().objects.select_for_update().get(pk=request.user.pk)
            recent_count = OwnerInputRequest.objects.filter(
                owner=owner,
                created_at__gte=now - timedelta(hours=1),
            ).count()
            if recent_count >= OWNER_REQUESTS_PER_HOUR:
                form.add_error(None, "Request limit reached. Please try again later.")
            else:
                item = form.save(commit=False)
                item.request_id = uuid4()
                item.owner = owner
                item.status = OwnerInputRequest.Status.QUEUED
                item.save()
                # Never log or echo the submitted body into application logs.
                messages.success(
                    request,
                    "Your request was queued for review. Submission does not execute it.",
                )
                return redirect("owner_console")

    recent_requests = OwnerInputRequest.objects.filter(
        owner=request.user
    ).only("request_id", "category", "title", "status", "created_at")[:10]
    return render(
        request,
        "core/owner_console.html",
        {
            "form": form,
            "recent_requests": recent_requests,
            "owner_username": request.user.get_username(),
            "device_binding_active": False,
        },
    )
