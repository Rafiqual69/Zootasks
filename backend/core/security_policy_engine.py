"""Runtime Policy Decision Point (PDP) for protected ZooTasks operations.

The PDP only grants a permit when exactly one applicable policy rule allows
the request and every declared condition is supplied by trusted server-side
facts. Missing, unknown, conflicting, or malformed inputs deny.
"""
from __future__ import annotations

from typing import Any, Mapping

from .security_policy import SecurityPolicyError, load_and_validate_policy


class AuthorizationDenied(PermissionError):
    """Raised when a protected operation cannot be explicitly authorized."""


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
) -> bool:
    """Return True only for an explicit, fully satisfied allow rule.

    facts must be produced by trusted server-side code. Client-supplied role,
    ownership, financial state, or privilege claims must never be passed here.
    """
    if not all(isinstance(value, str) and value for value in
               (actor, resource, action, scope)):
        return False

    trusted_facts = facts or {}
    if not isinstance(trusted_facts, Mapping):
        return False
    if any(not isinstance(key, str) or not isinstance(value, bool)
           for key, value in trusted_facts.items()):
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
