from django.test import SimpleTestCase

from core.ai_provider_offer_tests import sample_offer
from core.ai_provider_offer import validate_and_normalize_offer
from core.ai_worker_eligibility import (
    WorkerEligibilityProfile,
    evaluate_worker_eligibility,
)


class AIWorkerEligibilityTests(SimpleTestCase):
    def setUp(self):
        self.offer = validate_and_normalize_offer(sample_offer())

    def profile(self):
        return WorkerEligibilityProfile(
            region="BD",
            languages=frozenset({"bn", "en"}),
            skills=frozenset({"reasoning", "en"}),
            completed_qualifications=frozenset({"provider test"}),
        )

    def test_matching_worker_is_eligible_for_executable_offer(self):
        decision = evaluate_worker_eligibility(self.offer, self.profile())
        self.assertTrue(decision.eligible)
        self.assertEqual(decision.reasons, ())

    def test_non_executable_offer_is_denied(self):
        raw = sample_offer()
        raw["authorization"]["status"] = "pending"
        offer = validate_and_normalize_offer(raw)
        decision = evaluate_worker_eligibility(offer, self.profile())
        self.assertFalse(decision.eligible)
        self.assertIn("offer_not_executable", decision.reasons)

    def test_region_and_language_are_fail_closed(self):
        profile = WorkerEligibilityProfile(
            region="GB",
            languages=frozenset({"fr"}),
            skills=frozenset({"reasoning", "en"}),
            completed_qualifications=frozenset({"provider test"}),
        )
        decision = evaluate_worker_eligibility(self.offer, profile)
        self.assertFalse(decision.eligible)
        self.assertIn("region_not_eligible", decision.reasons)
        self.assertIn("language_not_eligible", decision.reasons)

    def test_missing_skill_denies_eligibility(self):
        profile = WorkerEligibilityProfile(
            region="BD",
            languages=frozenset({"en"}),
            skills=frozenset({"en"}),
            completed_qualifications=frozenset({"provider test"}),
        )
        decision = evaluate_worker_eligibility(self.offer, profile)
        self.assertFalse(decision.eligible)
        self.assertIn("skills_missing", decision.reasons)

    def test_missing_qualification_denies_eligibility(self):
        profile = WorkerEligibilityProfile(
            region="BD",
            languages=frozenset({"en"}),
            skills=frozenset({"reasoning", "en"}),
        )
        decision = evaluate_worker_eligibility(self.offer, profile)
        self.assertFalse(decision.eligible)
        self.assertIn("qualification_missing", decision.reasons)

    def test_casefolding_does_not_change_eligibility(self):
        profile = WorkerEligibilityProfile(
            region="bd",
            languages=frozenset({"EN"}),
            skills=frozenset({"REASONING", "en"}),
            completed_qualifications=frozenset({"PROVIDER TEST"}),
        )
        decision = evaluate_worker_eligibility(self.offer, profile)
        self.assertTrue(decision.eligible)
