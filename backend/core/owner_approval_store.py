"""Atomic persistence boundary for trusted Owner approvals."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from .models import OwnerApproval


class OwnerApprovalDenied(PermissionError):
    """Raised when an Owner approval cannot be consumed safely."""


@transaction.atomic
def consume_owner_approval(
    *,
    approval_id: UUID,
    owner_id: int,
    request_digest: str,
    now: datetime | None = None,
) -> OwnerApproval:
    """Atomically consume one valid approval exactly once.

    The caller must only invoke this after independently verifying the
    phishing-resistant authenticator assertion. The database row is locked so
    concurrent requests cannot both consume the same approval.
    """
    if not isinstance(request_digest, str) or not request_digest:
        raise OwnerApprovalDenied("Owner approval denied.")

    current_time = now or timezone.now()
    approval = (
        OwnerApproval.objects.select_for_update()
        .filter(
            approval_id=approval_id,
            owner_id=owner_id,
            request_digest=request_digest,
            consumed_at__isnull=True,
            revoked_at__isnull=True,
            expires_at__gt=current_time,
        )
        .first()
    )
    if approval is None:
        raise OwnerApprovalDenied("Owner approval denied.")

    approval.consumed_at = current_time
    approval.save(update_fields=("consumed_at",))
    return approval
