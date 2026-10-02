"""Deterministic provider-offer change detection.

Material provider changes fail closed into review/quarantine rather than silently
continuing execution. This module is intentionally network-free.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .ai_provider_offer import CanonicalOffer, validate_and_normalize_offer

MATERIAL_PATHS = (
    "provider.provider_id",
    "provider.name",
    "authorization.status",
    "authorization.route",
    "authorization.contract_reference",
    "source.kind",
    "source.identifier",
    "eligibility.regions",
    "eligibility.languages",
    "eligibility.requirements",
    "task.category",
    "data_policy.sensitivity",
    "data_policy.retention",
    "data_policy.processing_restrictions",
    "qualification.required",
    "qualification.method",
    "verification.method",
    "adapter.adapter_id",
    "adapter.version",
    "reward.amount",
    "reward.currency",
    "reward.payment_terms",
)

@dataclass(frozen=True)
class OfferChangeDecision:
    changed: bool
    material_fields: tuple[str, ...]
    action: str

    @property
    def requires_review(self) -> bool:
        return self.action == "review_required"

def _payload(value: CanonicalOffer | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(value, CanonicalOffer):
        return value.payload
    return validate_and_normalize_offer(value).payload

def _get(payload: Mapping[str, Any], path: str) -> Any:
    current: Any = payload
    for part in path.split("."):
        if not isinstance(current, Mapping):
            return None
        current = current.get(part)
    return current

def detect_offer_changes(
    previous: CanonicalOffer | Mapping[str, Any],
    candidate: CanonicalOffer | Mapping[str, Any],
) -> OfferChangeDecision:
    """Compare normalized offers and quarantine material changes.

    The comparison is intentionally limited to the declared material contract.
    Non-material metadata changes do not trigger review here.
    """
    before = _payload(previous)
    after = _payload(candidate)
    changed = tuple(path for path in MATERIAL_PATHS if _get(before, path) != _get(after, path))
    return OfferChangeDecision(
        changed=bool(changed),
        material_fields=changed,
        action="review_required" if changed else "unchanged",
    )
