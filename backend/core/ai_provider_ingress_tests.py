from django.test import SimpleTestCase

from core.ai_provider_ingress import (
    AIProviderIngressError,
    quarantine_offer_candidate,
    release_quarantined_offer,
)
from core.ai_provider_offer_tests import sample_offer


class AIProviderIngressTests(SimpleTestCase):
    def test_valid_candidate_is_always_quarantined(self):
        decision = quarantine_offer_candidate(sample_offer())
        self.assertEqual(decision.status, "quarantined")
        self.assertIsNotNone(decision.offer)
        self.assertFalse(decision.offer.executable)
        self.assertEqual(decision.offer.payload["risk"]["state"], "quarantined")

    def test_invalid_candidate_is_quarantined_without_raw_payload(self):
        candidate = sample_offer()
        candidate["task"]["category"] = "wallet_payout"
        decision = quarantine_offer_candidate(candidate)
        self.assertEqual(decision.status, "quarantined")
        self.assertIsNone(decision.offer)
        self.assertEqual(decision.reason, "offer_task_category_unsupported")

    def test_digest_is_deterministic(self):
        a = quarantine_offer_candidate(sample_offer())
        b = quarantine_offer_candidate(sample_offer())
        self.assertEqual(a.candidate_digest, b.candidate_digest)

    def test_candidate_change_changes_digest(self):
        a = sample_offer()
        b = sample_offer()
        b["reward"]["amount"] = 2
        self.assertNotEqual(
            quarantine_offer_candidate(a).candidate_digest,
            quarantine_offer_candidate(b).candidate_digest,
        )

    def test_quarantine_cannot_be_released_directly(self):
        decision = quarantine_offer_candidate(sample_offer())
        with self.assertRaisesRegex(
            AIProviderIngressError, "quarantine_release_requires_activation_gate"
        ):
            release_quarantined_offer(decision)
