from django.test import SimpleTestCase

from core.ai_privacy_gate import PrivacyGateError, PrivacyPolicy, evaluate_privacy


class AIPrivacyGateTests(SimpleTestCase):
    def test_unapproved_region_is_quarantined(self):
        policy = PrivacyPolicy(
            sensitivity="personal",
            purpose="task classification",
            retention="15 minutes",
            processing_restrictions=("no resale",),
            approved_regions=("EU",),
            approved=True,
        )
        decision = evaluate_privacy(policy, region="US")
        self.assertEqual(decision.state, "quarantined")

    def test_unapproved_privacy_review_is_quarantined(self):
        policy = PrivacyPolicy(
            sensitivity="internal",
            purpose="task quality assistance",
            retention="15 minutes",
            processing_restrictions=(),
            approved_regions=("US",),
            approved=False,
        )
        decision = evaluate_privacy(policy, region="US")
        self.assertEqual(decision.state, "quarantined")

    def test_invalid_sensitivity_fails_closed(self):
        policy = PrivacyPolicy(
            sensitivity="secret",
            purpose="x",
            retention="x",
            processing_restrictions=(),
            approved_regions=("US",),
            approved=True,
        )
        with self.assertRaisesRegex(PrivacyGateError, "privacy_sensitivity_invalid"):
            evaluate_privacy(policy, region="US")
