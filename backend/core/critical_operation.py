"""Execution-time gate for production critical operations.

This boundary joins exact request binding, atomic paired Owner approval
consumption, and the runtime policy decision. Callers must execute the actual
protected mutation inside the same outer transaction so a failed mutation
rolls back approval consumption.
"""
from __future__ import annotations

from collections.abc import Mapping
from uuid import UUID

from django.db import transaction

from .owner_approval_pair_store import (
    OwnerApprovalPairDenied,
    consume_owner_approval_pair,
)
from .owner_request_binding import canonical_request_digest
from .security_policy_engine import AuthorizationDenied, require_authorized


@transaction.atomic
def require_critical_operation_authorized(
    *,
    owner_id: int,
    approval_ids: tuple[UUID, UUID],
    request_id: str,
    operation: str,
    target: str,
    scope: str,
    environment: str,
    policy_version: str,
    material_parameters: Mapping[str, object] | None,
    actor: str,
    resource: str,
    action: str,
    authorization_scope: str,
    authorization_facts: Mapping[str, bool] | None = None,
) -> str:
    """Consume a bound approval pair and authorize the exact operation.

    The returned digest is the immutable binding evidence for the caller's
    audit event. authorization_facts must contain only trusted, server-derived
    boolean facts from the execution boundary; client input must never
    populate this mapping. The dual-control fact is injected only after the
    approval pair has been atomically consumed. The caller must perform the
    protected mutation in this same transaction context and must not substitute
    client-supplied parameters after this function returns.
    """
    digest = canonical_request_digest(
        request_id=request_id,
        operation=operation,
        target=target,
        scope=scope,
        environment=environment,
        policy_version=policy_version,
        material_parameters=material_parameters,
    )

    trusted_facts = dict(authorization_facts or {})
    if any(not isinstance(key, str) or not isinstance(value, bool)
           for key, value in trusted_facts.items()):
        raise AuthorizationDenied("Protected operation denied.")
    if "owner_dual_control_verified" in trusted_facts:
        raise AuthorizationDenied("Protected operation denied.")

    try:
        consume_owner_approval_pair(
            approval_ids=approval_ids,
            owner_id=owner_id,
            request_digest=digest,
        )
    except OwnerApprovalPairDenied as exc:
        raise AuthorizationDenied("Protected operation denied.") from exc

    trusted_facts["owner_dual_control_verified"] = True
    require_authorized(
        actor=actor,
        resource=resource,
        action=action,
        scope=authorization_scope,
        facts=trusted_facts,
    )
    return digest
