"""Fail-closed tool permission gateway for ZooTasks AI agents."""

from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet


class AIToolPermissionError(Exception):
    """Expected failure at the AI tool authorization boundary."""


@dataclass(frozen=True)
class AIToolPolicy:
    agent_id: str
    capability_id: str
    allowed_tool_classes: FrozenSet[str]
    max_calls: int
    external_side_effects: bool


TASK_QUALITY_TOOL_POLICY = AIToolPolicy(
    agent_id="ZT-AGENT-001",
    capability_id="AI-SYS-001",
    allowed_tool_classes=frozenset(),
    max_calls=0,
    external_side_effects=False,
)


def validate_tool_permission(
    *,
    agent_id: str,
    capability_id: str,
    tool_class: str,
    call_count: int = 0,
    external_side_effects: bool = False,
) -> None:
    policy = TASK_QUALITY_TOOL_POLICY
    if agent_id != policy.agent_id:
        raise AIToolPermissionError("ai_tool_agent_not_allowed")
    if capability_id != policy.capability_id:
        raise AIToolPermissionError("ai_tool_capability_not_allowed")
    if tool_class not in policy.allowed_tool_classes:
        raise AIToolPermissionError("ai_tool_not_allowed")
    if call_count >= policy.max_calls:
        raise AIToolPermissionError("ai_tool_budget_exceeded")
    if external_side_effects and not policy.external_side_effects:
        raise AIToolPermissionError("ai_tool_external_side_effect_forbidden")
