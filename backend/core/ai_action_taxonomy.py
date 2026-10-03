"""Deterministic action taxonomy for ZooTasks AI capabilities.

The taxonomy classifies proposed AI actions before any application workflow can
consider them. Classification is not authorization; privileged and financial
actions remain permanently forbidden to AI.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet


class AIActionTaxonomyError(ValueError):
    pass


IMPACT_LEVELS: FrozenSet[str] = frozenset(
    {"informational", "moderate", "high", "irreversible"}
)

FORBIDDEN_ACTIONS: FrozenSet[str] = frozenset(
    {
        "wallet_mutation",
        "withdrawal_approval",
        "withdrawal_payment",
        "promotion_payout",
        "task_reward_mutation",
        "permission_change",
        "owner_authentication",
        "identity_binding",
        "production_activation",
        "external_side_effect",
    }
)


@dataclass(frozen=True)
class ActionClass:
    action: str
    impact: str
    autonomous: bool
    human_approval_required: bool


_ACTIONS = {
    "read_analysis": ActionClass("read_analysis", "informational", True, False),
    "draft_briefing": ActionClass("draft_briefing", "informational", True, False),
    "classify_task": ActionClass("classify_task", "informational", True, False),
    "quality_suggestion": ActionClass("quality_suggestion", "moderate", False, True),
    "research": ActionClass("research", "informational", True, False),
    "draft_outreach": ActionClass("draft_outreach", "moderate", False, True),
    "wallet_mutation": ActionClass("wallet_mutation", "irreversible", False, True),
    "withdrawal_approval": ActionClass("withdrawal_approval", "high", False, True),
    "withdrawal_payment": ActionClass("withdrawal_payment", "irreversible", False, True),
    "promotion_payout": ActionClass("promotion_payout", "irreversible", False, True),
    "task_reward_mutation": ActionClass("task_reward_mutation", "high", False, True),
    "permission_change": ActionClass("permission_change", "high", False, True),
    "owner_authentication": ActionClass("owner_authentication", "high", False, True),
    "identity_binding": ActionClass("identity_binding", "high", False, True),
    "production_activation": ActionClass("production_activation", "irreversible", False, True),
    "external_side_effect": ActionClass("external_side_effect", "high", False, True),
}


def classify_action(action: str) -> ActionClass:
    action = str(action or "").strip()
    if not action:
        raise AIActionTaxonomyError("ai_action_required")
    if action not in _ACTIONS:
        raise AIActionTaxonomyError("ai_action_unknown")
    return _ACTIONS[action]


def validate_action_for_ai(action: str) -> ActionClass:
    classified = classify_action(action)
    if action in FORBIDDEN_ACTIONS:
        raise AIActionTaxonomyError("ai_action_forbidden")
    return classified
