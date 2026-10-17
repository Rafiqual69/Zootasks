"""Deterministic circuit breakers for bounded AI automation."""
from __future__ import annotations

from dataclasses import dataclass

from .ai_control_plane import AIGuardError

MAX_PLAN_COST_UNITS = 100
MAX_STEP_COST_UNITS = 25
MAX_CUMULATIVE_RETRIES = 12

@dataclass(frozen=True)
class AICostBudget:
    max_cost_units: int = MAX_PLAN_COST_UNITS
    max_tool_calls: int = 12
    max_retries: int = MAX_CUMULATIVE_RETRIES

def validate_ai_budget(*, cost_units: int, tool_calls: int, retries: int, budget: AICostBudget = AICostBudget()) -> None:
    """Reject unbounded execution; this never grants authorization."""
    values = (cost_units, tool_calls, retries, budget.max_cost_units, budget.max_tool_calls, budget.max_retries)
    if not all(isinstance(value, int) and value >= 0 for value in values):
        raise AIGuardError("AI execution budget is invalid.")
    if cost_units > budget.max_cost_units:
        raise AIGuardError("AI cost circuit breaker tripped.")
    if tool_calls > budget.max_tool_calls:
        raise AIGuardError("AI tool-call circuit breaker tripped.")
    if retries > budget.max_retries:
        raise AIGuardError("AI retry circuit breaker tripped.")

def validate_step_cost(cost_units: int) -> None:
    if not isinstance(cost_units, int) or cost_units < 0 or cost_units > MAX_STEP_COST_UNITS:
        raise AIGuardError("AI step cost circuit breaker tripped.")
