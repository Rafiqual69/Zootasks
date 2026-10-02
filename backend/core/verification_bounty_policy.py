"""Deterministic verification-bounty policy.

Design-only baseline. Reward calculation and payout remain outside this module.
"""


@dataclass(frozen=True)
class VerificationInput:
    submission_worker_id: int
    verifier_worker_id: int
    submission_id: str
    verifier_id: str
    same_worker: bool = False
    duplicate_verification: bool = False
    collusion_flag: bool = False
    verifier_active: bool = True
    reward_units: int = 0


from dataclasses import dataclass

MAX_VERIFICATION_REWARD_UNITS = 100


def validate_verification_assignment(item: VerificationInput) -> None:
    if not item.submission_id.strip() or not item.verifier_id.strip():
        raise ValueError("verification_identity_required")
    if item.submission_worker_id <= 0 or item.verifier_worker_id <= 0:
        raise ValueError("invalid_worker_identity")
    if item.reward_units < 0 or item.reward_units > MAX_VERIFICATION_REWARD_UNITS:
        raise ValueError("verification_reward_out_of_bounds")
    if not item.verifier_active:
        raise ValueError("verifier_not_active")
    if item.same_worker or item.submission_worker_id == item.verifier_worker_id:
        raise ValueError("self_verification_denied")
    if item.duplicate_verification:
        raise ValueError("duplicate_verification_denied")
    if item.collusion_flag:
        raise ValueError("collusion_review_required")


def verification_outcome_allowed(*, agreement: bool, escalation_required: bool) -> str:
    if escalation_required:
        return "escalate"
    return "verified" if agreement else "disputed"
