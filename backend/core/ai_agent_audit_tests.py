from django.test import SimpleTestCase

from .ai_agent_audit import AIAuditError, build_provenance_receipt


class AIAgentAuditTests(SimpleTestCase):
    def test_receipt_contains_only_metadata_and_hash(self):
        receipt = build_provenance_receipt({
            "agent_id": "ZT-AGENT-001",
            "capability_id": "AI-SYS-001",
            "correlation_id": "corr-1",
            "data_class": "task_content_minimal",
            "policy_version": "1.0",
            "decision": "suggestion",
        })
        self.assertEqual(receipt["schema_version"], "1.0")
        self.assertEqual(len(receipt["receipt_sha256"]), 64)
        self.assertNotIn("prompt", receipt)
        self.assertNotIn("output", receipt)

    def test_unknown_raw_content_field_is_rejected(self):
        with self.assertRaisesMessage(AIAuditError, "ai_audit_unknown_field"):
            build_provenance_receipt({
                "agent_id": "ZT-AGENT-001",
                "capability_id": "AI-SYS-001",
                "correlation_id": "corr-1",
                "decision": "suggestion",
                "prompt": "secret",
            })

    def test_required_metadata_is_enforced(self):
        with self.assertRaisesMessage(AIAuditError, "ai_audit_required_field_missing"):
            build_provenance_receipt({
                "agent_id": "ZT-AGENT-001",
                "capability_id": "AI-SYS-001",
                "correlation_id": "",
                "decision": "suggestion",
            })
