"""Network-free provider adapter boundary.

Production adapters are intentionally absent. This interface only validates a
read-only adapter contract and provides a deterministic synthetic adapter for CI.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence

from .ai_provider_offer import CanonicalOffer, validate_and_normalize_offer
from .ai_provider_registry import ProviderRegistration, can_sync_provider


class AIProviderAdapterError(ValueError):
    pass


@dataclass(frozen=True)
class AdapterContext:
    provider: ProviderRegistration
    max_offers: int = 50

    def validate(self) -> None:
        if not can_sync_provider(self.provider):
            raise AIProviderAdapterError("provider_sync_not_authorized")
        if not isinstance(self.max_offers, int) or isinstance(self.max_offers, bool):
            raise AIProviderAdapterError("max_offers_invalid")
        if self.max_offers < 1 or self.max_offers > 100:
            raise AIProviderAdapterError("max_offers_out_of_bounds")


class ReadOnlyProviderAdapter(Protocol):
    adapter_id: str
    adapter_version: str

    def sync_offers(self, context: AdapterContext) -> Sequence[Mapping[str, Any]]:
        ...


@dataclass(frozen=True)
class SyntheticProviderAdapter:
    """CI fixture only; it performs no network access or side effects."""
    adapter_id: str = "synthetic-ci"
    adapter_version: str = "1.0"

    def sync_offers(self, context: AdapterContext) -> Sequence[Mapping[str, Any]]:
        context.validate()
        if context.provider.adapter_id != self.adapter_id:
            raise AIProviderAdapterError("adapter_identity_mismatch")
        if context.provider.adapter_version != self.adapter_version:
            raise AIProviderAdapterError("adapter_version_mismatch")
        return ()

def validate_adapter_candidate(
    candidate: Mapping[str, Any],
    context: AdapterContext,
) -> CanonicalOffer:
    """Normalize untrusted adapter output without granting execution authority."""
    context.validate()
    return validate_and_normalize_offer(candidate)
