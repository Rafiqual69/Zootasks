"""Deterministic capability gate for future ZooTasks AI agents.

This module authorizes capability *requests* only. It never executes tools or
mutates application state. Default is deny and financial mutation is forbidden.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet


class AgentCapabilityError(Exception):
    """Expected fail-closed agent capability rejection."""


FORBIDDEN_ACTIONS: FrozenSet[str] = frozenset({
    "wallet_mutation",
    "withdrawal_approval",
    "withdrawal_payment",
    "promotion_payout",
    "task_reward_mutation",
    "permission_change",
    "owner_authentication",
    "identity_binding",
})


@dataclass(frozen=True)
class AgentCapability:
    capability_id: str
    agent_id: str
    allowed_actions: FrozenSet[str]
    allowed_tools: FrozenSet[str] = frozenset()
    allowed_destinations: FrozenSet[str] = frozenset()
    max_tool_calls: int = 0
    max_external_side_effects: int = 0
    requires_human_approval: bool = False


@dataclass(frozen=True)
class AgentCapabilityRequest:
    agent_id: str
    capability_id: str
    action: str
    tool: str | None = None
    destination: str | None = None
    approved: bool = False


def authorize_capability(
    capability: AgentCapability,
    request: AgentCapabilityRequest,
) -> None:
    """Fail closed unless the request exactly fits the registered contract."""
    if request.agent_id != capability.agent_id:
        raise AgentCapabilityError("agent_identity_mismatch")
    if request.capability_id != capability.capability_id:
        raise AgentCapabilityError("agent_capability_mismatch")
    if request.action in FORBIDDEN_ACTIONS:
        raise AgentCapabilityError("agent_action_forbidden")
    if request.action not in capability.allowed_actions:
        raise AgentCapabilityError("agent_action_not_allowed")

    if request.tool is not None and request.tool not in capability.allowed_tools:
        raise AgentCapabilityError("agent_tool_not_allowed")
    if request.destination is not None and request.destination not in capability.allowed_destinations:
        raise AgentCapabilityError("agent_destination_not_allowed")

    if capability.requires_human_approval and not request.approved:
        raise AgentCapabilityError("agent_human_approval_required")


def registered_capabilities() -> tuple[AgentCapability, ...]:
    """Return only the currently registered design-stage capabilities."""
    return (
        AgentCapability(
            capability_id="AGENT-EXEC-001",
            agent_id="executive-advisor",
            allowed_actions=frozenset({"read_analysis", "draft_briefing", "escalate"}),
            allowed_tools=frozenset({"approved_research"}),
            max_tool_calls=20,
            max_external_side_effects=0,
            requires_human_approval=False,
        ),
        AgentCapability(
            capability_id="AGENT-ACQ-001",
            agent_id="business-acquisition",
            allowed_actions=frozenset({"research", "draft_outreach"}),
            allowed_tools=frozenset({"approved_research"}),
            max_tool_calls=10,
            max_external_side_effects=0,
            requires_human_approval=True,
        ),
    )
