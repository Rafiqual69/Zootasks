"""Fail-closed ingress quarantine for discovered provider offers.

Ingress is an untrusted boundary. It never activates an offer, grants provider
authorization, enables an adapter, or performs network/financial side effects.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping
import hashlib
import json

from .ai_provider_offer import CanonicalOffer, AIProviderOfferError, validate_and_normalize_offer


class AIProviderIngressError(ValueError):
    pass


@dataclass(frozen=True)
class IngressDecision:
    status: str
    candidate_digest: str
    offer: CanonicalOffer | None
    reason: str


def _digest(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def quarantine_offer_candidate(candidate: Mapping[str, Any]) -> IngressDecision:
    """Validate a discovered candidate and keep it quarantined."""
    if not isinstance(candidate, Mapping):
        raise AIProviderIngressError("ingress_candidate_invalid")
    digest = _digest(candidate)
    try:
        normalized = validate_and_normalize_offer(candidate)
    except AIProviderOfferError as exc:
        return IngressDecision("quarantined", digest, None, str(exc))

    payload = dict(normalized.payload)
    payload["risk"] = {"state": "quarantined", "reason": "ingress_pending_review"}
    return IngressDecision("quarantined", digest, CanonicalOffer(payload), "ingress_pending_review")


def release_quarantined_offer(decision: IngressDecision) -> CanonicalOffer:
    """Reject implicit release; activation belongs to a later gate."""
    if decision.status != "quarantined" or decision.offer is None:
        raise AIProviderIngressError("quarantine_release_invalid")
    raise AIProviderIngressError("quarantine_release_requires_activation_gate")
