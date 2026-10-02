"""Deterministic safety policy for ZooTasks AI automation.

The firewall is intentionally provider-neutral and fail-closed. It does not
execute tools, mutate business state, or make authorization decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet


class AISafetyFirewallError(Exception):
    """Expected failure at the AI action-policy boundary."""


@dataclass(frozen=True)
class AICapabilityPolicy:
    capability_id: str
    max_autonomy: str
    allowed_action_classes: FrozenSet[str]


TASK_QUALITY_POLICY = AICapabilityPolicy(
    capability_id="AI-SYS-001",
    max_autonomy="suggestion_only",
    allowed_action_classes=frozenset({"suggestion"}),
)

FORBIDDEN_ACTION_CLASSES = frozenset(
    {
        "wallet_mutation",
        "withdrawal_approval",
        "withdrawal_payment",
        "promotion_payout",
        "task_reward_mutation",
        "permission_change",
        "owner_authentication",
        "identity_binding",
        "external_side_effect",
    }
)


def get_capability_policy(capability_id: str) -> AICapabilityPolicy:
    if capability_id != TASK_QUALITY_POLICY.capability_id:
        raise AISafetyFirewallError("ai_capability_policy_not_found")
    return TASK_QUALITY_POLICY


def validate_action_class(*, capability_id: str, action_class: str) -> None:
    policy = get_capability_policy(capability_id)
    if not action_class or action_class in FORBIDDEN_ACTION_CLASSES:
        raise AISafetyFirewallError("ai_action_class_forbidden")
    if action_class not in policy.allowed_action_classes:
        raise AISafetyFirewallError("ai_action_class_not_allowed")


def validate_autonomy(*, capability_id: str, autonomy: str) -> None:
    policy = get_capability_policy(capability_id)
    if autonomy != policy.max_autonomy:
        raise AISafetyFirewallError("ai_autonomy_not_allowed")
