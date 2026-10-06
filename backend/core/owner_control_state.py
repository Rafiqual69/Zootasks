"""Fail-closed production state model for Owner dual control."""
from __future__ import annotations

from enum import StrEnum


class OwnerControlState(StrEnum):
    DEVELOPMENT_SINGLE_DEVICE = "DEVELOPMENT_SINGLE_DEVICE"
    PRODUCTION_READINESS_PENDING = "PRODUCTION_READINESS_PENDING"
    PRODUCTION_DUAL_CONTROL = "PRODUCTION_DUAL_CONTROL"
    SECURITY_FREEZE = "SECURITY_FREEZE"


class OwnerControlStateDenied(PermissionError):
    """Raised when state cannot authorize a protected production operation."""


def parse_owner_control_state(value: str) -> OwnerControlState:
    """Parse only known states; unknown or malformed state fails closed."""
    if not isinstance(value, str):
        raise OwnerControlStateDenied("Owner control state denied.")
    try:
        return OwnerControlState(value)
    except ValueError as exc:
        raise OwnerControlStateDenied("Owner control state denied.") from exc


def requires_dual_control(*, state: OwnerControlState, protected_production: bool) -> bool:
    """Return whether a protected production action needs the dual-control ceremony."""
    if not isinstance(state, OwnerControlState):
        raise OwnerControlStateDenied("Owner control state denied.")
    if not isinstance(protected_production, bool):
        raise OwnerControlStateDenied("Owner control state denied.")
    if not protected_production:
        return False
    if state is OwnerControlState.PRODUCTION_DUAL_CONTROL:
        return True
    raise OwnerControlStateDenied("Owner control state denied.")
