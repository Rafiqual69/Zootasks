"""Execution-time authorization bridge for protected application mutations.

Development keeps the existing policy path. Production critical operations
must present a server-created Owner approval pair in the authenticated session;
this module never creates, trusts, or accepts approval IDs from request body,
query parameters, or arbitrary client facts.
"""
from __future__ import annotations

from uuid import UUID

from django.http import HttpRequest

from .critical_operation import require_critical_operation_authorized
from .security_policy_engine import CRITICAL_PRODUCTION_OPERATIONS, _production_mode, require_authorized\nfrom .security_policy import load_and_validate_policy


_APPROVAL_SESSION_KEY = "_zt_owner_approval_pair"


def _server_approval_context(request: HttpRequest) -> tuple[str, tuple[UUID, UUID]] | None:
    """Read only the server-side approval context created by the ceremony."""
    try:
        raw = request.session.get(_APPROVAL_SESSION_KEY)
    except Exception:
        return None
    if not isinstance(raw, dict):
        return None
    request_id = raw.get("request_id")
    approval_values = raw.get("approval_ids")
    if not isinstance(request_id, str) or not request_id:
        return None
    if not isinstance(approval_values, (list, tuple)) or len(approval_values) != 2:
        return None
    try:
        first, second = (UUID(str(value)) for value in approval_values)
    except (TypeError, ValueError):
        return None
    if first == second:
        return None
    return request_id, (first, second)


def require_execution_authorized(
    *,
    request: HttpRequest,
    owner_id: int,
    operation: str,
    target: str,
    scope: str,
    environment: str,
    policy_version: str,
    material_parameters: dict[str, object],
    actor: str,
    resource: str,
    action: str,
    authorization_scope: str,
    authorization_facts: dict[str, bool],
) -> str | None:
    """Authorize one mutation at its execution boundary.

    In development/non-production, the existing policy path remains available.
    In production, critical operations require a server-created approval pair.
    The pair is consumed by the exact-request-bound critical-operation gate.
    Missing/malformed session context therefore fails closed.
    """
    if not isinstance(owner_id, int) or owner_id <= 0:
        raise PermissionError("Protected operation denied.")

    from .security_policy_engine import CRITICAL_PRODUCTION_OPERATIONS, _production_mode

    critical = (actor, resource, action, authorization_scope) in CRITICAL_PRODUCTION_OPERATIONS
    if not _production_mode() or not critical:
        require_authorized(
            actor=actor,
            resource=resource,
            action=action,
            scope=authorization_scope,
            facts=authorization_facts,
        )
        return None

    approval_context = _server_approval_context(request)
    if approval_context is None:
        raise PermissionError("Protected operation denied.")
    request_id, approval_ids = approval_context

    digest = require_critical_operation_authorized(
        owner_id=owner_id,
        approval_ids=approval_ids,
        request_id=request_id,
        operation=operation,
        target=target,
        scope=scope,
        environment=environment,
        policy_version=policy_version,
        material_parameters=material_parameters,
        actor=actor,
        resource=resource,
        action=action,
        authorization_scope=authorization_scope,
        authorization_facts=authorization_facts,
    )

    # A consumed pair must never remain reusable in the session.
    try:
        request.session.pop(_APPROVAL_SESSION_KEY, None)
        request.session.save()
    except Exception as exc:
        # Fail closed: the operation must not succeed if the one-time context
        # cannot be retired from the authenticated server-side session.
        raise PermissionError("Protected operation denied.") from exc

    return digest
