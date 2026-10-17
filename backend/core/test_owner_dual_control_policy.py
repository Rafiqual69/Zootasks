import json
from pathlib import Path
import unittest


POLICY_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "security"
    / "owner_dual_control_policy.json"
)


class OwnerDualControlPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with POLICY_PATH.open("r", encoding="utf-8") as handle:
            cls.policy = json.load(handle)

    def test_policy_is_fail_closed_and_proposed(self):
        self.assertEqual(self.policy["status"], "proposed")
        self.assertEqual(self.policy["activation"], "production_readiness_gate")
        self.assertEqual(self.policy["default_decision"], "deny")
        self.assertEqual(self.policy["approval_model"], "two_independent_owner_devices")

    def test_development_mode_preserves_current_owner_device(self):
        mode = self.policy["current_development_mode"]
        self.assertTrue(mode["existing_owner_device_allowed"])
        self.assertFalse(mode["dual_control_required"])
        self.assertEqual(mode["scope"], "non_production_development_operations_only")

    def test_critical_operations_are_protected(self):
        required = {
            "production_deploy",
            "production_rollback",
            "security_policy_change",
            "owner_privilege_change",
            "authentication_control_change",
            "migration_promotion",
            "recovery_promotion",
            "financial_write",
            "withdrawal_approval",
            "withdrawal_payment",
            "network_exposure_change",
            "irreversible_deletion",
            "break_glass_operation",
        }
        self.assertTrue(required.issubset(self.policy["protected_operations"]))

    def test_security_requirements_cannot_be_weakened(self):
        requirements = self.policy["requirements"]
        for key in (
            "independent_device_identities",
            "phishing_resistant_authentication",
            "action_binding",
            "target_binding",
            "parameter_binding",
            "short_lived_approval",
            "replay_protection",
            "revocation",
            "execution_time_reauthorization",
            "audit_metadata_without_secrets",
        ):
            self.assertIs(requirements[key], True)

    def test_automation_cannot_create_or_execute_without_owner_approvals(self):
        automation = self.policy["automation"]
        self.assertTrue(automation["may_prepare_request"])
        self.assertTrue(automation["may_validate_request"])
        self.assertIs(automation["may_execute_dual_control_action_without_two_owner_approvals"], False)
        self.assertIs(automation["may_create_or_replay_owner_approval"], False)
        self.assertIs(self.policy["human_approval_required"], True)

    def test_deny_conditions_include_compromise_and_gate_failures(self):
        conditions = set(self.policy["deny_conditions"])
        self.assertIn("missing_second_approval", conditions)
        self.assertIn("duplicate_or_replayed_approval", conditions)
        self.assertIn("approval_parameter_mismatch", conditions)
        self.assertIn("failed_required_ci", conditions)
        self.assertIn("failed_required_review", conditions)
        self.assertIn("active_security_freeze", conditions)
        self.assertIn("suspected_single_anchor_compromise", conditions)
        self.assertIn("secret_exposure_risk", conditions)


if __name__ == "__main__":
    unittest.main()
