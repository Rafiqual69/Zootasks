"""Deterministic registry for ZooTasks AI agents.

Agents are identified independently from models/providers. The registry defines
least-privilege capability, data, autonomy, and tool boundaries. It performs
no network calls and never grants business authorization.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet


class AIAgentRegistryError(Exception):
    """Expected failure at the AI agent control boundary."""


@dataclass(frozen=True)
class AIAgentPolicy:
    agent_id: str
    capability_ids: FrozenSet[str]
    allowed_data_classes: FrozenSet[str]
    allowed_tool_classes: FrozenSet[str]
    max_autonomy: str


TASK_QUALITY_AGENT = AIAgentPolicy(
    agent_id="ZT-AGENT-001",
    capability_ids=frozenset({"AI-SYS-001"}),
    allowed_data_classes=frozenset({"task_content_minimal"}),
    allowed_tool_classes=frozenset(),
    max_autonomy="suggestion_only",
)


def get_agent_policy(agent_id: str) -> AIAgentPolicy:
    if agent_id != TASK_QUALITY_AGENT.agent_id:
        raise AIAgentRegistryError("ai_agent_not_registered")
    return TASK_QUALITY_AGENT


def validate_agent_capability(*, agent_id: str, capability_id: str) -> None:
    policy = get_agent_policy(agent_id)
    if capability_id not in policy.capability_ids:
        raise AIAgentRegistryError("ai_agent_capability_not_allowed")


def validate_agent_data_class(*, agent_id: str, data_class: str) -> None:
    policy = get_agent_policy(agent_id)
    if data_class not in policy.allowed_data_classes:
        raise AIAgentRegistryError("ai_agent_data_class_not_allowed")


def validate_agent_tool(*, agent_id: str, tool_class: str) -> None:
    policy = get_agent_policy(agent_id)
    if tool_class not in policy.allowed_tool_classes:
        raise AIAgentRegistryError("ai_agent_tool_not_allowed")


def validate_agent_autonomy(*, agent_id: str, autonomy: str) -> None:
    policy = get_agent_policy(agent_id)
    if autonomy != policy.max_autonomy:
        raise AIAgentRegistryError("ai_agent_autonomy_not_allowed")