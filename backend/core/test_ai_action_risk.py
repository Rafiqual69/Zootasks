from django.test import SimpleTestCase

from .ai_action_risk import AIRiskLevel, classify_ai_action, requires_human_governance


class AIActionRiskTests(SimpleTestCase):
    def test_unknown_action_fails_closed_to_high(self):
        self.assertEqual(
            classify_ai_action("future_unregistered_action"),
            AIRiskLevel.HIGH,
        )

    def test_malformed_action_fails_closed(self):
        self.assertEqual(classify_ai_action(""), AIRiskLevel.HIGH)
        self.assertEqual(classify_ai_action(None), AIRiskLevel.HIGH)

    def test_financial_actions_are_critical(self):
        for action in (
            "modify_wallet_balance",
            "approve_payout",
            "pay_withdrawal",
            "run_production_migration",
        ):
            self.assertEqual(classify_ai_action(action), AIRiskLevel.CRITICAL)
            self.assertTrue(requires_human_governance(action))

    def test_low_risk_read_action_does_not_require_human_governance(self):
        self.assertEqual(
            classify_ai_action("read_scoped_project_data"),
            AIRiskLevel.LOW,
        )
        self.assertFalse(requires_human_governance("read_scoped_project_data"))
