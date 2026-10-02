from django.test import SimpleTestCase

from .ai_provider_change_detection import detect_offer_changes


def _offer(**overrides):
    data = {
        "schema_version": "1.0",
        "offer_id": "OFFER-001",
        "provider": {"provider_id": "provider-a", "name": "Provider A"},
        "authorization": {"status": "verified", "route": "api_partner", "contract_reference": "C-1"},
        "source": {"kind": "api", "identifier": "api:v1/offers"},
        "eligibility": {"regions": ["BD"], "languages": ["en"], "requirements": ["age>=18"]},
        "task": {"category": "llm_evaluation", "title": "Evaluate outputs", "skills": ["English"]},
        "reward": {"amount": "1.00", "currency": "USD", "payment_terms": "net-30"},
        "data_policy": {"sensitivity": "internal", "retention": "30d", "processing_restrictions": ["no_export"]},
        "qualification": {"required": True, "method": "test"},
        "verification": {"method": "double_review"},
        "adapter": {"adapter_id": "adapter-a", "version": "1.0"},
        "sync": {"status": "active", "last_success_at": "2026-10-02T00:00:00Z"},
        "provenance": {"source_revision": "rev-1", "evidence_refs": ["E1"]},
        "risk": {"state": "approved", "reason": None},
    }
    for key, value in overrides.items():
        data[key] = value
    return data


class ProviderOfferChangeDetectionTests(SimpleTestCase):
    def test_identical_offers_are_unchanged(self):
        decision = detect_offer_changes(_offer(), _offer())
        self.assertFalse(decision.changed)
        self.assertEqual(decision.material_fields, ())
        self.assertFalse(decision.requires_review)

    def test_reward_change_requires_review(self):
        candidate = _offer(reward={"amount": "2.00", "currency": "USD", "payment_terms": "net-30"})
        decision = detect_offer_changes(_offer(), candidate)
        self.assertTrue(decision.requires_review)
        self.assertEqual(decision.material_fields, ("reward.amount",))

    def test_authorization_change_requires_review(self):
        candidate = _offer(authorization={"status": "pending", "route": "api_partner", "contract_reference": "C-1"})
        decision = detect_offer_changes(_offer(), candidate)
        self.assertEqual(decision.material_fields, ("authorization.status",))

    def test_region_change_requires_review(self):
        candidate = _offer(eligibility={"regions": ["BD", "US"], "languages": ["en"], "requirements": ["age>=18"]})
        decision = detect_offer_changes(_offer(), candidate)
        self.assertEqual(decision.material_fields, ("eligibility.regions",))

    def test_non_material_title_change_does_not_require_review(self):
        candidate = _offer(task={"category": "llm_evaluation", "title": "New display title", "skills": ["English"]})
        decision = detect_offer_changes(_offer(), candidate)
        self.assertFalse(decision.requires_review)
        self.assertEqual(decision.material_fields, ())

    def test_multiple_material_changes_are_sorted_by_contract_order(self):
        candidate = _offer(
            reward={"amount": "2.00", "currency": "EUR", "payment_terms": "prepaid"},
            adapter={"adapter_id": "adapter-a", "version": "2.0"},
        )
        decision = detect_offer_changes(_offer(), candidate)
        self.assertEqual(
            decision.material_fields,
            ("adapter.version", "reward.amount", "reward.currency", "reward.payment_terms"),
        )

    def test_invalid_candidate_fails_closed(self):
        candidate = _offer(reward={"amount": "-1", "currency": "USD", "payment_terms": "net-30"})
        with self.assertRaises(ValueError):
            detect_offer_changes(_offer(), candidate)
