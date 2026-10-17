"""Atomic paired-consumption boundary for Owner dual-control approvals."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from .models import OwnerApproval


class OwnerApprovalPairDenied(PermissionError):
    """Raised when two approvals cannot be consumed as one authorization."""


@transaction.atomic
def consume_owner_approval_pair(
    *,
    approval_ids: tuple[UUID, UUID],
    owner_id: int,
    request_digest: str,
    now: datetime | None = None,
    incident_freeze: bool = False,
) -> tuple[OwnerApproval, OwnerApproval]:
    """Lock and consume exactly two independent approvals atomically."""
    if incident_freeze or len(approval_ids) != 2 or approval_ids[0] == approval_ids[1]:
        raise OwnerApprovalPairDenied("Owner approval denied.")
    if not isinstance(request_digest, str) or not request_digest:
        raise OwnerApprovalPairDenied("Owner approval denied.")

    current_time = now or timezone.now()
    rows = list(
        OwnerApproval.objects.select_for_update()
        .filter(
            approval_id__in=approval_ids,
            owner_id=owner_id,
            request_digest=request_digest,
            consumed_at__isnull=True,
            revoked_at__isnull=True,
            expires_at__gt=current_time,
        )
        .order_by("approval_id")
    )
    if len(rows) != 2:
        raise OwnerApprovalPairDenied("Owner approval denied.")
    if rows[0].device_id == rows[1].device_id:
        raise OwnerApprovalPairDenied("Owner approval denied.")
    if rows[0].credential_id == rows[1].credential_id:
        raise OwnerApprovalPairDenied("Owner approval denied.")

    for row in rows:
        row.consumed_at = current_time
        row.save(update_fields=("consumed_at",))
    return rows[0], rows[1]
