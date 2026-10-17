"""Fail-closed risk classification for AI-proposed actions.

This module is deliberately independent from model output. It classifies an
already-normalized action name so the execution layer can require stronger
authorization for higher-risk operations.
"""

from enum import StrEnum


class AIRiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Explicit allowlist: unknown actions are HIGH rather than LOW.
AI_ACTION_RISK = {
    "read_public_data": AIRiskLevel.LOW,
    "read_scoped_project_data": AIRiskLevel.LOW,
    "generate_report": AIRiskLevel.LOW,
    "create_draft": AIRiskLevel.MEDIUM,
    "write_nonfinancial_record": AIRiskLevel.MEDIUM,
    "send_external_message": AIRiskLevel.HIGH,
    "change_access_policy": AIRiskLevel.CRITICAL,
    "change_privileged_credentials": AIRiskLevel.CRITICAL,
    "modify_wallet_balance": AIRiskLevel.CRITICAL,
    "approve_payout": AIRiskLevel.CRITICAL,
    "pay_withdrawal": AIRiskLevel.CRITICAL,
    "run_production_migration": AIRiskLevel.CRITICAL,
    "delete_production_data": AIRiskLevel.CRITICAL,
}


def classify_ai_action(action: str) -> AIRiskLevel:
    """Return the minimum risk level required for an AI-proposed action.

    Unknown or malformed actions fail closed to HIGH.
    """
    if not isinstance(action, str):
        return AIRiskLevel.HIGH
    normalized = action.strip().lower()
    if not normalized:
        return AIRiskLevel.HIGH
    return AI_ACTION_RISK.get(normalized, AIRiskLevel.HIGH)


def requires_human_governance(action: str) -> bool:
    """Critical actions always require human governance."""
    return classify_ai_action(action) is AIRiskLevel.CRITICAL
