from django.test import SimpleTestCase

from .ai_safety_firewall import (
    AISafetyFirewallError,
    validate_action_class,
    validate_autonomy,
)


class AISafetyFirewallTests(SimpleTestCase):
    def test_task_quality_allows_only_suggestions(self):
        validate_action_class(capability_id="AI-SYS-001", action_class="suggestion")
        validate_autonomy(capability_id="AI-SYS-001", autonomy="suggestion_only")

    def test_financial_action_is_forbidden(self):
        with self.assertRaisesMessage(AISafetyFirewallError, "ai_action_class_forbidden"):
            validate_action_class(
                capability_id="AI-SYS-001",
                action_class="withdrawal_payment",
            )

    def test_unknown_action_class_is_denied(self):
        with self.assertRaisesMessage(AISafetyFirewallError, "ai_action_class_not_allowed"):
            validate_action_class(
                capability_id="AI-SYS-001",
                action_class="tool_execution",
            )

    def test_higher_autonomy_is_denied(self):
        with self.assertRaisesMessage(AISafetyFirewallError, "ai_autonomy_not_allowed"):
            validate_autonomy(
                capability_id="AI-SYS-001",
                autonomy="autonomous_execution",
            )

    def test_unknown_capability_has_no_policy(self):
        with self.assertRaisesMessage(AISafetyFirewallError, "ai_capability_policy_not_found"):
            validate_action_class(
                capability_id="AI-SYS-999",
                action_class="suggestion",
            )
