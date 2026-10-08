"""Runtime Policy Decision Point (PDP) for protected ZooTasks operations.

The PDP only grants a permit when exactly one applicable policy rule allows
the request and every declared condition is supplied by trusted server-side
facts. Missing, unknown, conflicting, or malformed inputs deny.

Production critical operations have an additional fail-closed dual-control
overlay. The verified approval ceremony must set the trusted
owner_dual_control_verified fact only after server-side verification and
atomic consumption of two independent Owner approvals.
"""
from __future__ import annotations

import os
from typing import Any, Mapping

from django.conf import settings

from .owner_control_state import (
    OwnerControlState,
    OwnerControlStateDenied,
    requires_dual_control,
)
from .security_policy import SecurityPolicyError, load_and_validate_policy


class AuthorizationDenied(PermissionError):
    """Raised when a protected operation cannot be explicitly authorized."""


class _SystemAutomationCapability:
    __slots__ = ()


SYSTEM_AUTOMATION_CAPABILITY = _SystemAutomationCapability()


CRITICAL_PRODUCTION_OPERATIONS = frozenset({
    ("owner", "task", "create", "global"),
    ("owner", "task", "update", "global"),
    ("owner", "promotion", "create", "global"),
    ("owner", "promotion", "update", "global"),
    ("finance", "task_claim", "approve", "role_scope"),
    ("finance", "task_claim", "reject", "role_scope"),
    ("finance", "promotion_claim", "approve", "role_scope"),
    ("finance", "promotion_claim", "reject", "role_scope"),
    ("finance", "withdrawal", "approve", "role_scope"),
    ("finance", "withdrawal", "reject", "role_scope"),
    ("finance_payer", "withdrawal", "pay", "role_scope"),
})


def _production_mode() -> bool:
    """Resolve production mode; malformed configuration fails closed."""
    raw = os.environ.get("PRODUCTION_MODE")
    if raw is None:
        raw = getattr(settings, "PRODUCTION_MODE", False)
    if isinstance(raw, bool):
        return raw
    value = str(raw).strip().lower()
    if value == "true":
        return True
    if value == "false":
        return False
    raise AuthorizationDenied("Protected operation denied.")


def _production_dual_control_allows(
    *,
    actor: str,
    resource: str,
    action: str,
    scope: str,
    facts: Mapping[str, bool],
) -> bool:
    if (actor, resource, action, scope) not in CRITICAL_PRODUCTION_OPERATIONS:
        return True
    if not _production_mode():
        return True

    state_value = os.environ.get(
        "OWNER_CONTROL_STATE",
        OwnerControlState.PRODUCTION_READINESS_PENDING.value,
    )
    try:
        state = OwnerControlState(state_value)
        if not requires_dual_control(state=state, protected_production=True):
            return False
    except (ValueError, OwnerControlStateDenied):
        return False

    return facts.get("owner_dual_control_verified") is True


def _rule_matches(rule: Mapping[str, Any], *, actor: str, resource: str,
                  action: str, scope: str, facts: Mapping[str, Any]) -> bool:
    if (
        rule["actor"] != actor
        or rule["resource"] != resource
        or rule["action"] != action
        or rule["scope"] != scope
        or rule["decision"] != "allow"
    ):
        return False
    return all(facts.get(condition) is True for condition in rule["conditions"])


def authorize(
    *,
    actor: str,
    resource: str,
    action: str,
    scope: str,
    facts: Mapping[str, Any] | None = None,
    system_capability: object | None = None,
) -> bool:
    """Return True only for an explicit, fully satisfied allow rule."""
    if not all(isinstance(value, str) and value for value in
               (actor, resource, action, scope)):
        return False

    try:
        _production_mode()
    except AuthorizationDenied:
        return False

    if actor == "system" and system_capability is not SYSTEM_AUTOMATION_CAPABILITY:
        return False

    if actor == "system" and system_capability is not SYSTEM_AUTOMATION_CAPABILITY:
        return False

    trusted_facts = facts or {}
    if not isinstance(trusted_facts, Mapping):
        return False
    if any(not isinstance(key, str) or not isinstance(value, bool)
           for key, value in trusted_facts.items()):
        return False

    try:
        if not _production_dual_control_allows(
            actor=actor,
            resource=resource,
            action=action,
            scope=scope,
            facts=trusted_facts,
        ):
            return False
    except AuthorizationDenied:
        return False

    try:
        policy = load_and_validate_policy()
    except SecurityPolicyError:
        return False

    rules = policy["rules"]
    applicable = [
        rule for rule in rules
        if rule["actor"] == actor
        and rule["resource"] == resource
        and rule["action"] == action
        and rule["scope"] == scope
    ]

    if len(applicable) != 1:
        return False

    return _rule_matches(
        applicable[0],
        actor=actor,
        resource=resource,
        action=action,
        scope=scope,
        facts=trusted_facts,
    )


def require_authorized(**kwargs: Any) -> None:
    if not authorize(**kwargs):
        raise AuthorizationDenied("Protected operation denied.")
