from django.test import SimpleTestCase

from .ai_provider_adapter import (
    AdapterContext,
    AIProviderAdapterError,
    SyntheticProviderAdapter,
    validate_adapter_candidate,
)
from .ai_provider_registry import ProviderRegistration


def _provider(**kw):
    base = dict(
        provider_id="p1", name="Provider", route="api_partner", status="verified",
        adapter_id="synthetic-ci", adapter_version="1.0",
        allowed_regions=frozenset({"BD"}), capabilities=frozenset({"offer_sync"}),
        adapter_state="ready",
    )
    base.update(kw)
    return ProviderRegistration(**base)


class ProviderAdapterTests(SimpleTestCase):
    def test_synthetic_adapter_is_read_only_and_network_free(self):
        result = SyntheticProviderAdapter().sync_offers(AdapterContext(_provider()))
        self.assertEqual(result, ())

    def test_unverified_provider_cannot_sync(self):
        with self.assertRaises(AIProviderAdapterError):
            SyntheticProviderAdapter().sync_offers(
                AdapterContext(_provider(status="pending", adapter_state="disabled"))
            )

    def test_adapter_identity_must_match_registration(self):
        with self.assertRaises(AIProviderAdapterError):
            SyntheticProviderAdapter().sync_offers(
                AdapterContext(_provider(adapter_id="other", adapter_state="ready"))
            )

    def test_offer_candidate_is_normalized_but_not_authorized(self):
        candidate = {
            "schema_version": "1.0", "offer_id": "O1",
            "provider": {"provider_id": "p1", "name": "Provider"},
            "authorization": {"status": "verified", "route": "api_partner"},
            "source": {"kind": "api", "identifier": "synthetic"},
            "eligibility": {"regions": ["BD"], "languages": ["en"], "requirements": []},
            "task": {"category": "llm_evaluation", "title": "Test", "skills": []},
            "reward": {"amount": "1", "currency": "USD", "payment_terms": "net-30"},
            "data_policy": {"sensitivity": "internal", "retention": "30d", "processing_restrictions": []},
            "qualification": {"required": False, "method": "none"},
            "verification": {"method": "deterministic"},
            "adapter": {"adapter_id": "synthetic-ci", "version": "1.0"},
            "sync": {"status": "active", "last_success_at": "2026-10-02T00:00:00Z"},
            "provenance": {"source_revision": "r1", "evidence_refs": []},
            "risk": {"state": "approved", "reason": None},
        }
        offer = validate_adapter_candidate(candidate, AdapterContext(_provider()))
        self.assertEqual(offer.offer_id, "O1")
        self.assertFalse(getattr(offer, "execution_authorized", False))

    def test_budget_is_bounded(self):
        with self.assertRaises(AIProviderAdapterError):
            AdapterContext(_provider(), max_offers=101).validate()
