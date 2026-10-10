from unittest.mock import patch

from django.core.cache import cache
from django.test import SimpleTestCase

from .ai_agent_trust import (
    AIAgentRequest,
    AIAgentTrustError,
    sign_inter_agent_request,
    verify_inter_agent_request,
)


class AIAgentTrustTests(SimpleTestCase):
    def setUp(self):
        cache.clear()

    def request(self, **overrides):
        values = {
            "sender": "research-agent",
            "receiver": "execution-gateway",
            "request_id": "req-100",
            "request_digest": "a" * 64,
            "nonce": "nonce-100-unique-value",
            "issued_at": 1000,
            "expires_at": 1100,
            "claims": {"operation": "generate_report"},
            "signature": "",
        }
        values.update(overrides)
        request = AIAgentRequest(**values)
        if not request.signature:
            request = AIAgentRequest(**{**values, "signature": sign_inter_agent_request(request)})
        return request

    @patch.dict("os.environ", {"AI_AGENT_TRUST_KEY": "test-only-key-with-at-least-32-bytes"}, clear=False)
    def test_valid_request_is_accepted_once(self):
        request = self.request()
        verify_inter_agent_request(request, expected_receiver="execution-gateway", now=1050)
        with self.assertRaises(AIAgentTrustError):
            verify_inter_agent_request(request, expected_receiver="execution-gateway", now=1050)

    @patch.dict("os.environ", {"AI_AGENT_TRUST_KEY": "test-only-key-with-at-least-32-bytes"}, clear=False)
    def test_tampering_is_rejected(self):
        request = self.request(claims={"operation": "read_scoped_project_data"})
        tampered = AIAgentRequest(**{**request.__dict__, "request_digest": "b" * 64})
        with self.assertRaises(AIAgentTrustError):
            verify_inter_agent_request(tampered, expected_receiver="execution-gateway", now=1050)

    @patch.dict("os.environ", {"AI_AGENT_TRUST_KEY": "test-only-key-with-at-least-32-bytes"}, clear=False)
    def test_wrong_receiver_is_rejected(self):
        with self.assertRaises(AIAgentTrustError):
            verify_inter_agent_request(self.request(receiver="other-gateway"), expected_receiver="execution-gateway", now=1050)

    @patch.dict("os.environ", {"AI_AGENT_TRUST_KEY": "test-only-key-with-at-least-32-bytes"}, clear=False)
    def test_upstream_approval_claim_is_never_authority(self):
        request = self.request(claims={"authorized": True})
        request = AIAgentRequest(**{**request.__dict__, "signature": sign_inter_agent_request(request)})
        with self.assertRaises(AIAgentTrustError):
            verify_inter_agent_request(request, expected_receiver="execution-gateway", now=1050)

    @patch.dict("os.environ", {}, clear=True)
    def test_missing_trust_key_fails_closed(self):
        with self.assertRaises(AIAgentTrustError):
            sign_inter_agent_request(self.request(signature="not-used"))

    @patch.dict("os.environ", {"AI_AGENT_TRUST_KEY": "short"}, clear=False)
    def test_short_trust_key_fails_closed(self):
        with self.assertRaises(AIAgentTrustError):
            sign_inter_agent_request(self.request())

    @patch.dict("os.environ", {"AI_AGENT_TRUST_KEY": "test-only-key-with-at-least-32-bytes"}, clear=False)
    def test_oversized_nested_claims_are_rejected(self):
        nested = "x"
        for _ in range(7):
            nested = {"nested": nested}
        with self.assertRaises(AIAgentTrustError):
            verify_inter_agent_request(
                self.request(claims=nested), expected_receiver="execution-gateway", now=1050,
            )

    @patch.dict("os.environ", {"AI_AGENT_TRUST_KEY": "test-only-key-with-at-least-32-bytes"}, clear=False)
    def test_replay_store_failure_fails_closed(self):
        request = self.request()
        with patch("core.ai_agent_trust.cache.add", side_effect=RuntimeError("cache unavailable")):
            with self.assertRaises(AIAgentTrustError):
                verify_inter_agent_request(request, expected_receiver="execution-gateway", now=1050)

    @patch.dict("os.environ", {"AI_AGENT_TRUST_KEY": "test-only-key-with-at-least-32-bytes"}, clear=False)
    def test_short_nonce_is_rejected(self):
        request = self.request(nonce="short")
        with self.assertRaises(AIAgentTrustError):
            verify_inter_agent_request(request, expected_receiver="execution-gateway", now=1050)

    @patch.dict("os.environ", {"AI_AGENT_TRUST_KEY": "test-only-key-with-at-least-32-bytes"}, clear=False)
    def test_malformed_nonce_format_is_rejected(self):
        request = self.request(nonce="nonce with spaces!!")
        with self.assertRaises(AIAgentTrustError):
            verify_inter_agent_request(request, expected_receiver="execution-gateway", now=1050)

    @patch.dict("os.environ", {"AI_AGENT_TRUST_KEY": "test-only-key-with-at-least-32-bytes"}, clear=False)
    def test_oversized_claim_key_is_rejected(self):
        request = self.request(claims={"k" * 129: "value"})
        with self.assertRaises(AIAgentTrustError):
            verify_inter_agent_request(request, expected_receiver="execution-gateway", now=1050)

    @patch.dict("os.environ", {"AI_AGENT_TRUST_KEY": "test-only-key-with-at-least-32-bytes"}, clear=False)
    def test_boolean_timestamps_are_rejected(self):
        request = self.request(issued_at=True, expires_at=1100)
        with self.assertRaises(AIAgentTrustError):
            verify_inter_agent_request(request, expected_receiver="execution-gateway", now=1050)

    @patch.dict("os.environ", {"AI_AGENT_TRUST_KEY": "test-only-key-with-at-least-32-bytes"}, clear=False)
    def test_malformed_request_digest_is_rejected(self):
        request = self.request(request_digest="not-a-sha256-digest")
        with self.assertRaises(AIAgentTrustError):
            verify_inter_agent_request(request, expected_receiver="execution-gateway", now=1050)

    @patch.dict("os.environ", {"AI_AGENT_TRUST_KEY": "test-only-key-with-at-least-32-bytes"}, clear=False)
    def test_oversized_sender_metadata_is_rejected(self):
        request = self.request(sender="s" * 129)
        with self.assertRaises(AIAgentTrustError):
            verify_inter_agent_request(request, expected_receiver="execution-gateway", now=1050)

    @patch.dict("os.environ", {"AI_AGENT_TRUST_KEY": "test-only-key-with-at-least-32-bytes"}, clear=False)
    def test_expired_request_is_rejected(self):
        with self.assertRaises(AIAgentTrustError):
            verify_inter_agent_request(self.request(), expected_receiver="execution-gateway", now=2000)
