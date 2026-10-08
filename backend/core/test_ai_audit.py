from django.test import SimpleTestCase

from .ai_action_risk import AIRiskLevel
from .ai_audit import AIDataTrust, build_ai_audit_event

class AIAuditTests(SimpleTestCase):
    def test_safe_metadata_excludes_payload_fields(self):
        event = build_ai_audit_event(
            request_digest="a" * 64, decision="denied", risk=AIRiskLevel.HIGH,
            tool="send_external_message", action="send_external_message",
            target="project:messaging", scope="message:review",
            policy_version="1.0.0", data_trust=AIDataTrust.UNTRUSTED_DATA,
        )
        safe = event.to_safe_dict()
        self.assertEqual(safe["risk"], "high")
        self.assertEqual(safe["data_trust"], "untrusted_data")
        self.assertNotIn("prompt", safe)
        self.assertNotIn("parameters", safe)
        self.assertNotIn("payload", safe)

    def test_invalid_digest_is_rejected(self):
        with self.assertRaises(ValueError):
            build_ai_audit_event(
                request_digest="short", decision="denied", risk=AIRiskLevel.HIGH,
                tool="x", action="x", target="x", scope="x",
                policy_version="1.0.0", data_trust=AIDataTrust.TOOL_OUTPUT,
            )
