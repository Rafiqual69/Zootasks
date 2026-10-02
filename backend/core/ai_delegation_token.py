"""Deterministic scoped delegation boundary for multi-agent calls."""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json

class DelegationError(ValueError):
    pass

FORBIDDEN=frozenset({"wallet_mutation","withdrawal_approval","withdrawal_payment","promotion_payout","permission_change","owner_authentication","identity_binding","production_activation","external_side_effect"})

@dataclass(frozen=True)
class Delegation:
    delegation_id: str
    issuer_agent_id: str
    subject_agent_id: str
    actions: tuple[str, ...]
    tools: tuple[str, ...]
    destinations: tuple[str, ...]
    max_calls: int
    expires_at: str
    approval_ref: str | None = None

def validate_delegation(d: Delegation) -> None:
    if not d.delegation_id.strip() or not d.issuer_agent_id.strip() or not d.subject_agent_id.strip():
        raise DelegationError("delegation_identity_required")
    if not d.actions or not d.tools or not d.expires_at.strip():
        raise DelegationError("delegation_scope_required")
    if d.max_calls < 1 or d.max_calls > 100:
        raise DelegationError("delegation_call_budget_invalid")
    if set(d.actions) & FORBIDDEN:
        raise DelegationError("delegation_forbidden_action")
    if any(not x.strip() for x in d.actions+d.tools+d.destinations):
        raise DelegationError("delegation_scope_invalid")
    if d.issuer_agent_id == d.subject_agent_id:
        raise DelegationError("self_delegation_not_allowed")

def delegation_digest(d: Delegation) -> str:
    validate_delegation(d)
    payload={k:getattr(d,k) for k in ("delegation_id","issuer_agent_id","subject_agent_id","actions","tools","destinations","max_calls","expires_at","approval_ref")}
    return sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def authorize_delegated_call(d: Delegation, *, action: str, tool: str, destination: str, calls_used: int) -> bool:
    validate_delegation(d)
    if calls_used < 0 or calls_used >= d.max_calls:
        raise DelegationError("delegation_call_budget_exceeded")
    if action not in d.actions:
        raise DelegationError("delegated_action_not_allowed")
    if tool not in d.tools:
        raise DelegationError("delegated_tool_not_allowed")
    if d.destinations and destination not in d.destinations:
        raise DelegationError("delegated_destination_not_allowed")
    return True
