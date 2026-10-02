"""Deterministic capability budgets for ZooTasks AI automation.

Budgets are hard limits, not provider hints. AI-SYS-001 has no tool calls or
external side effects and is bounded to suggestion-only output.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


class AICapabilityBudgetError(Exception):
    """Expected failure when an AI capability exceeds its deterministic budget."""


@dataclass(frozen=True)
class AICapabilityBudget:
    capability_id: str
    max_input_chars: int
    max_output_chars: int
    max_list_items: int
    max_tool_calls: int
    external_side_effects: bool


TASK_QUALITY_BUDGET = AICapabilityBudget(
    capability_id="AI-SYS-001",
    max_input_chars=12000,
    max_output_chars=3000,
    max_list_items=10,
    max_tool_calls=0,
    external_side_effects=False,
)


def get_capability_budget(capability_id: str) -> AICapabilityBudget:
    if capability_id != TASK_QUALITY_BUDGET.capability_id:
        raise AICapabilityBudgetError("ai_capability_budget_not_found")
    return TASK_QUALITY_BUDGET


def validate_input_budget(*, capability_id: str, input_data: Mapping[str, Any]) -> None:
    budget = get_capability_budget(capability_id)
    total = sum(len(value) for value in input_data.values() if isinstance(value, str))
    if total > budget.max_input_chars:
        raise AICapabilityBudgetError("ai_input_budget_exceeded")


def validate_output_budget(*, capability_id: str, output: Mapping[str, Any]) -> None:
    budget = get_capability_budget(capability_id)
    encoded_size = len(str(output).encode("utf-8"))
    if encoded_size > budget.max_output_chars:
        raise AICapabilityBudgetError("ai_output_budget_exceeded")
    for value in output.values():
        if isinstance(value, list) and len(value) > budget.max_list_items:
            raise AICapabilityBudgetError("ai_output_list_budget_exceeded")


def validate_execution_budget(*, capability_id: str, tool_calls: int, external_side_effects: bool) -> None:
    budget = get_capability_budget(capability_id)
    if tool_calls > budget.max_tool_calls:
        raise AICapabilityBudgetError("ai_tool_budget_exceeded")
    if external_side_effects and not budget.external_side_effects:
        raise AICapabilityBudgetError("ai_external_side_effect_forbidden")
