from django.test import SimpleTestCase

from core.ai_action_taxonomy import (
    AIActionTaxonomyError,
    classify_action,
    validate_action_for_ai,
)


class AIActionTaxonomyTests(SimpleTestCase):
    def test_safe_task_action_is_informational(self):
        action = validate_action_for_ai("classify_task")
        self.assertEqual(action.impact, "informational")
        self.assertTrue(action.autonomous)
        self.assertFalse(action.human_approval_required)

    def test_quality_suggestion_requires_review(self):
        action = validate_action_for_ai("quality_suggestion")
        self.assertEqual(action.impact, "moderate")
        self.assertFalse(action.autonomous)
        self.assertTrue(action.human_approval_required)

    def test_financial_actions_are_forbidden(self):
        for action in ("wallet_mutation", "withdrawal_approval", "withdrawal_payment", "promotion_payout"):
            with self.assertRaisesRegex(AIActionTaxonomyError, "ai_action_forbidden"):
                validate_action_for_ai(action)

    def test_unknown_action_fails_closed(self):
        with self.assertRaisesRegex(AIActionTaxonomyError, "ai_action_unknown"):
            classify_action("send_money")
