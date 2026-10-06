"""Fail-closed decision gate for ZooTasks Owner dual-control operations.

This module does not implement WebAuthn/passkeys or persist approvals. It consumes
ONLY trusted server-side verification results produced by the future authentication
and approval subsystem. Client-provided approval JSON must never be passed here
without independent verification.

The gate enforces the second layer: two distinct Owner device identities,
exact request binding, expiry/revocation/replay checks, and incident freeze.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Mapping


class DualControlDenied(PermissionError):
    """Raised when a protected operation lacks two valid independent approvals."""


@dataclass(frozen=True)
class VerifiedOwnerApproval:
    """Trusted result of an independent device approval verification."""

    approval_id: str
    device_id: str
    credential_id: str
    request_digest: str
    expires_at: datetime
    revoked: bool
    replay_detected: bool
    phishing_resistant: bool
    owner_authenticated: bool


def _valid_approval(
    approval: VerifiedOwnerApproval,
    *,
    request_digest: str,
    now: datetime,
) -> bool:
    """Check one already-verified approval without trusting client assertions."""
    return bool(
        approval.approval_id
        and approval.device_id
        and approval.credential_id
        and approval.request_digest == request_digest
        and approval.expires_at > now
        and not approval.revoked
        and not approval.replay_detected
        and approval.phishing_resistant
        and approval.owner_authenticated
    )


def authorize_dual_control(
    *,
    request_digest: str,
    approvals: tuple[VerifiedOwnerApproval, ...],
    now: datetime,
    incident_freeze: bool = False,
) -> bool:
    """Return True only when exactly two independent valid approvals exist.

    Independence is enforced by both device and credential identity. A second
    browser tab, duplicated credential, or repeated presentation of one device
    cannot satisfy the two-person rule.

    The caller remains responsible for:
    - verifying WebAuthn/passkey assertions before constructing approvals;
    - atomically consuming approval IDs/nonces to prevent races/replay;
    - re-authorizing the exact request immediately before execution.
    """
    if not isinstance(request_digest, str) or not request_digest:
        return False
    if incident_freeze or len(approvals) != 2:
        return False
    if any(not isinstance(item, VerifiedOwnerApproval) for item in approvals):
        return False

    first, second = approvals
    if first.device_id == second.device_id:
        return False
    if first.credential_id == second.credential_id:
        return False
    if first.approval_id == second.approval_id:
        return False

    return _valid_approval(first, request_digest=request_digest, now=now) and _valid_approval(
        second, request_digest=request_digest, now=now
    )


def require_dual_control(**kwargs: object) -> None:
    """Raise a non-sensitive denial for any failed dual-control decision."""
    if not authorize_dual_control(**kwargs):  # type: ignore[arg-type]
        raise DualControlDenied("Protected operation requires two independent Owner approvals.")
