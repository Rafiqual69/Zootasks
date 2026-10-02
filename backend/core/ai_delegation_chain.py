"""Fail-closed delegation-chain verification for ZooTasks agents."""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json

class DelegationChainError(ValueError):
    pass

@dataclass(frozen=True)
class ChainLink:
    delegation_id: str
    issuer_agent_id: str
    subject_agent_id: str
    actions: tuple[str, ...]
    tools: tuple[str, ...]
    destinations: tuple[str, ...]
    max_calls: int
    parent_digest: str | None = None

def _digest(link: ChainLink) -> str:
    payload={k:getattr(link,k) for k in (
        "delegation_id","issuer_agent_id","subject_agent_id","actions",
        "tools","destinations","max_calls","parent_digest")}
    return sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def verify_chain(chain: tuple[ChainLink, ...]) -> str:
    if not chain:
        raise DelegationChainError("delegation_chain_empty")
    previous=None
    for index, link in enumerate(chain):
        if not link.delegation_id.strip() or not link.issuer_agent_id.strip() or not link.subject_agent_id.strip():
            raise DelegationChainError("delegation_identity_required")
        if link.issuer_agent_id == link.subject_agent_id:
            raise DelegationChainError("self_delegation")
        if link.max_calls < 1 or link.max_calls > 100:
            raise DelegationChainError("delegation_budget_invalid")
        if not link.actions or not link.tools:
            raise DelegationChainError("delegation_scope_required")
        if any(not x.strip() for x in link.actions+link.tools+link.destinations):
            raise DelegationChainError("delegation_scope_invalid")
        if index == 0:
            if link.parent_digest is not None:
                raise DelegationChainError("root_parent_must_be_empty")
        else:
            if link.parent_digest != previous:
                raise DelegationChainError("delegation_parent_mismatch")
            parent=chain[index-1]
            if link.subject_agent_id != parent.subject_agent_id and link.issuer_agent_id != parent.subject_agent_id:
                raise DelegationChainError("delegation_issuer_chain_mismatch")
            if not set(link.actions).issubset(parent.actions):
                raise DelegationChainError("delegation_action_escalation")
            if not set(link.tools).issubset(parent.tools):
                raise DelegationChainError("delegation_tool_escalation")
            if not set(link.destinations).issubset(parent.destinations):
                raise DelegationChainError("delegation_destination_escalation")
            if link.max_calls > parent.max_calls:
                raise DelegationChainError("delegation_budget_escalation")
        previous=_digest(link)
    return previous
