"""Execution-time authorization bridge for protected financial/admin mutations.

Development keeps the existing server-side policy path. Production requires a
server-created exact-operation approval context and the atomic dual-control
gate. No client-provided approval values are accepted.
"""
from __future__ import annotations

from collections.abc import Mapping
from uuid import UUID

from django.conf import settings

from accounts.models import AccountEntity

from .critical_operation import require_critical_operation_authorized
from .security_policy import load_and_validate_policy
from .security_policy_engine import AuthorizationDenied, require_authorized

SESSION_KEY = "zt_critical_execution"


def _production_mode() -> bool:
    return bool(getattr(settings, "PRODUCTION_MODE", False))


def require_execution_authorized(
    *,
    request,
    operation: str,
    target: str,
    actor: str,
    resource: str,
    action: str,
    material_parameters: Mapping[str, object],
    authorization_facts: Mapping[str, bool],
) -> str | None:
    """Authorize the exact mutation immediately before it executes.

    In development this delegates to the existing policy engine. In production
    it requires the short-lived, server-created dual-control context stored in
    the authenticated session by the future approval ceremony.
    """
    if not request.user.is_authenticated:
        raise AuthorizationDenied("Protected operation denied.")

    if not _production_mode():
        require_authorized(
            actor=actor,
            resource=resource,
            action=action,
            scope="role_scope",
            facts=authorization_facts,
        )
        return None

    if getattr(settings, "OWNER_CONTROL_STATE", "") != "PRODUCTION_DUAL_CONTROL":
        raise AuthorizationDenied("Protected operation denied.")

    context = request.session.get(SESSION_KEY)
    if not isinstance(context, dict):
        raise AuthorizationDenied("Protected operation denied.")

    owner_id_raw = context.get("owner_id")
    request_id = context.get("request_id")
    approval_ids_raw = context.get("approval_ids")
    try:
        owner_id = int(owner_id_raw)
    except (TypeError, ValueError):
        raise AuthorizationDenied("Protected operation denied.")
    if not AccountEntity.objects.filter(
        user_id=owner_id,
        entity_type=AccountEntity.EntityType.OWNER,
        is_active=True,
    ).exists():
        raise AuthorizationDenied("Protected operation denied.")
    if not isinstance(request_id, str) or not request_id:
        raise AuthorizationDenied("Protected operation denied.")
    if not isinstance(approval_ids_raw, (list, tuple)) or len(approval_ids_raw) != 2:
        raise AuthorizationDenied("Protected operation denied.")

    try:
        approval_ids = tuple(UUID(str(value)) for value in approval_ids_raw)
    except (TypeError, ValueError, AttributeError) as exc:
        raise AuthorizationDenied("Protected operation denied.") from exc

    policy = load_and_validate_policy()
    digest = require_critical_operation_authorized(
        owner_id=owner_id,
        approval_ids=approval_ids,  # type: ignore[arg-type]
        request_id=request_id,
        operation=operation,
        target=target,
        scope="role_scope",
        environment="production",
        policy_version=policy["policy_version"],
        material_parameters=material_parameters,
        actor=actor,
        resource=resource,
        action=action,
        authorization_scope="role_scope",
        authorization_facts=authorization_facts,
    )
    request.session.pop(SESSION_KEY, None)
    request.session.modified = True
    return digest
