from django.test import SimpleTestCase

from core.ai_release_tevv_gate import ReleaseEvidence, ReleaseGateError, evaluate_release, release_digest


class AIReleaseTEVVGateTests(SimpleTestCase):
    def base(self, state="candidate", approval_ref=None):
        return ReleaseEvidence(
            release_id="REL-001",
            system_id="AI-SYS-001",
            code_revision="4829340",
            source_revision_digest="a" * 64,
            evaluation_digest="b" * 64,
            policy_bundle_digest="c" * 64,
            test_digest="d" * 64,
            rollback_ref="RB-001",
            monitoring_ref="MON-001",
            approval_ref=approval_ref,
            state=state,
        )

    def test_candidate_is_quarantined(self):
        evidence = self.base()
        state, digest = evaluate_release(evidence)
        self.assertEqual(state, "quarantined")
        self.assertEqual(len(digest), 64)

    def test_approved_release_requires_approval_reference(self):
        with self.assertRaisesRegex(ReleaseGateError, "release_approval_required"):
            release_digest(self.base(state="approved"))

    def test_approved_release_is_controlled_rollout(self):
        state, digest = evaluate_release(self.base(state="approved", approval_ref="APP-001"))
        self.assertEqual(state, "approved_for_controlled_rollout")
        self.assertEqual(len(digest), 64)
