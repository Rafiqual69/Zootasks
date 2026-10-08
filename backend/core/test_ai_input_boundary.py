from django.test import SimpleTestCase

from .ai_audit import AIDataTrust
from .ai_input_boundary import assert_data_never_authorizes, classify_ai_input

class AIInputBoundaryTests(SimpleTestCase):
    def test_known_sources_are_classified(self):
        self.assertEqual(classify_ai_input("memory"), AIDataTrust.MEMORY)
        self.assertEqual(classify_ai_input("untrusted_data"), AIDataTrust.UNTRUSTED_DATA)
        self.assertEqual(classify_ai_input("tool_output"), AIDataTrust.TOOL_OUTPUT)

    def test_unknown_source_fails_closed(self):
        with self.assertRaises(ValueError):
            classify_ai_input("prompt_injection")

    def test_external_data_cannot_grant_authority(self):
        for trust in (AIDataTrust.MEMORY, AIDataTrust.UNTRUSTED_DATA, AIDataTrust.TOOL_OUTPUT):
            with self.assertRaises(PermissionError):
                assert_data_never_authorizes(data_trust=trust, requested_authority="approve_payout")

    def test_instruction_is_not_an_authorization_grant(self):
        # This helper only classifies provenance; the real policy engine remains authoritative.
        assert_data_never_authorizes(data_trust=AIDataTrust.INSTRUCTION, requested_authority="create_draft")
