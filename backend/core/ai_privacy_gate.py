"""Fail-closed privacy and retention gate for provider capabilities."""
from __future__ import annotations
from dataclasses import dataclass

class PrivacyGateError(ValueError):
    pass

@dataclass(frozen=True)
class PrivacyPolicy:
    sensitivity: str
    purpose: str
    retention: str
    processing_restrictions: tuple[str, ...]
    approved_regions: tuple[str, ...]
    approved: bool = False

@dataclass(frozen=True)
class PrivacyDecision:
    state: str
    reasons: tuple[str, ...]

ALLOWED_SENSITIVITY={"public","internal","personal","sensitive","restricted"}

def evaluate_privacy(policy: PrivacyPolicy, *, region: str) -> PrivacyDecision:
    if policy.sensitivity not in ALLOWED_SENSITIVITY:
        raise PrivacyGateError("privacy_sensitivity_invalid")
    if not policy.purpose.strip() or not policy.retention.strip():
        raise PrivacyGateError("privacy_purpose_retention_required")
    if not policy.approved_regions or any(not x.strip() for x in policy.approved_regions):
        raise PrivacyGateError("privacy_region_policy_required")
    if region not in policy.approved_regions:
        return PrivacyDecision("quarantined",("region_not_approved",))
    if not policy.approved:
        return PrivacyDecision("quarantined",("privacy_review_required",))
    return PrivacyDecision("approved",("privacy_review_passed",))
