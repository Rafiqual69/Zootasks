"""Deterministic Quality Ladder policy for ZooTasks.

Design-only policy: no wallet mutation, payout, permission, or Owner action.
"""
from dataclasses import dataclass

LEVEL_NEW = "new"
LEVEL_QUALIFIED = "qualified"
LEVEL_TRUSTED = "trusted"
LEVEL_SPECIALIST = "specialist"

LEVELS = (LEVEL_NEW, LEVEL_QUALIFIED, LEVEL_TRUSTED, LEVEL_SPECIALIST)


@dataclass(frozen=True)
class QualityEvidence:
    qualification_passed: bool = False
    completed_tasks: int = 0
    quality_rate_basis_points: int = 0
    verified_tasks: int = 0
    fraud_flags: int = 0
    cooldown_active: bool = False


@dataclass(frozen=True)
class QualityThreshold:
    minimum_completed_tasks: int
    minimum_quality_rate_basis_points: int
    minimum_verified_tasks: int


THRESHOLDS = {
    LEVEL_QUALIFIED: QualityThreshold(1, 8000, 0),
    LEVEL_TRUSTED: QualityThreshold(10, 9000, 3),
    LEVEL_SPECIALIST: QualityThreshold(50, 9500, 10),
}


def calculate_quality_level(evidence: QualityEvidence) -> str:
    """Return the highest deterministic level supported by evidence."""
    if evidence.completed_tasks < 0 or evidence.quality_rate_basis_points < 0:
        raise ValueError("invalid_quality_evidence")
    if evidence.verified_tasks < 0 or evidence.fraud_flags < 0:
        raise ValueError("invalid_quality_evidence")
    if evidence.fraud_flags > 0 or evidence.cooldown_active:
        return LEVEL_NEW

    level = LEVEL_NEW
    if evidence.qualification_passed:
        threshold = THRESHOLDS[LEVEL_QUALIFIED]
        if (
            evidence.completed_tasks >= threshold.minimum_completed_tasks
            and evidence.quality_rate_basis_points >= threshold.minimum_quality_rate_basis_points
        ):
            level = LEVEL_QUALIFIED

    for candidate in (LEVEL_TRUSTED, LEVEL_SPECIALIST):
        threshold = THRESHOLDS[candidate]
        if (
            level != LEVEL_NEW
            and evidence.completed_tasks >= threshold.minimum_completed_tasks
            and evidence.quality_rate_basis_points >= threshold.minimum_quality_rate_basis_points
            and evidence.verified_tasks >= threshold.minimum_verified_tasks
        ):
            level = candidate
    return level
