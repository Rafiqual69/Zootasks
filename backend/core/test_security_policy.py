import copy
import json
import unittest
from pathlib import Path

from .security_policy import (
    POLICY_PATH,
    SCHEMA_PATH,
    SecurityPolicyError,
    load_and_validate_policy,
    validate_policy,
)


class SecurityPolicyContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = load_and_validate_policy()
        cls.schema = json.loads(Path(SCHEMA_PATH).read_text(encoding="utf-8"))

    def test_repository_policy_is_valid(self):
        self.assertEqual(self.policy["enforcement"]["default_decision"], "deny")

    def test_unknown_actor_is_rejected(self):
        policy = copy.deepcopy(self.policy)
        policy["rules"][0]["actor"] = "unknown"
        with self.assertRaises(SecurityPolicyError):
            validate_policy(policy, self.schema)

    def test_unknown_resource_is_rejected(self):
        policy = copy.deepcopy(self.policy)
        policy["rules"][0]["resource"] = "unknown"
        with self.assertRaises(SecurityPolicyError):
            validate_policy(policy, self.schema)

    def test_conflicting_allow_and_deny_is_rejected(self):
        policy = copy.deepcopy(self.policy)
        base = copy.deepcopy(policy["rules"][0])
        base["rule_id"] = "ZT-CONFLICT-TEST-001"
        policy["rules"].append(base)
        base["decision"] = "deny"
        base["rule_id"] = "ZT-CONFLICT-TEST-002"
        policy["rules"].append(base)
        with self.assertRaises(SecurityPolicyError):
            validate_policy(policy, self.schema)

    def test_ai_financial_allow_is_rejected(self):
        policy = copy.deepcopy(self.policy)
        rule = copy.deepcopy(next(r for r in policy["rules"] if r["actor"] == "ai"))
        rule.update(
            rule_id="ZT-AI-FINANCIAL-ALLOW-TEST",
            decision="allow",
            action="update",
            resource="wallet",
        )
        policy["rules"].append(rule)
        with self.assertRaises(SecurityPolicyError):
            validate_policy(policy, self.schema)

    def test_unsupported_policy_major_is_rejected(self):
        policy = copy.deepcopy(self.policy)
        policy["policy_version"] = "2.0.0"
        with self.assertRaises(SecurityPolicyError):
            validate_policy(policy, self.schema)

    def test_policy_loader_error_does_not_expose_filesystem_path(self):
        from unittest.mock import patch
        with patch("pathlib.Path.open", side_effect=OSError("private-path-error")):
            with self.assertRaises(SecurityPolicyError) as captured:
                load_and_validate_policy()
        self.assertNotIn(str(POLICY_PATH), str(captured.exception))
        self.assertNotIn(str(SCHEMA_PATH), str(captured.exception))

    def test_parse_failure_is_rejected(self):
        policy = copy.deepcopy(self.policy)
        policy["enforcement"]["policy_parse_failure"] = "allow"
        with self.assertRaises(SecurityPolicyError):
            validate_policy(policy, self.schema)

    def test_data_disclosure_controls_cannot_be_weakened(self):
        policy = copy.deepcopy(self.policy)
        policy["data_handling"]["response_allowlist_only"] = False
        with self.assertRaises(SecurityPolicyError):
            validate_policy(policy, self.schema)

    def test_client_cannot_control_sensitive_fields(self):
        policy = copy.deepcopy(self.policy)
        policy["data_handling"]["client_controls_sensitive_fields"] = True
        with self.assertRaises(SecurityPolicyError):
            validate_policy(policy, self.schema)

    def test_model_field_alignment_is_required(self):
        policy = copy.deepcopy(self.policy)
        policy["data_handling"]["actual_model_field_alignment"] = False
        with self.assertRaises(SecurityPolicyError):
            validate_policy(policy, self.schema)

    def test_financial_identity_fields_are_complete(self):
        policy = copy.deepcopy(self.policy)
        policy["data_handling"]["protected_financial_identity_fields"] = ["user_id"]
        with self.assertRaises(SecurityPolicyError):
            validate_policy(policy, self.schema)


if __name__ == "__main__":
    unittest.main()

