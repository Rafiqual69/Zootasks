from django.test import SimpleTestCase
from core.ai_innovation_loop import InnovationGateError, InnovationProposal, evaluate_innovation, promote_innovation_candidate
def proposal(**overrides):
    data=dict(proposal_id="INNO-001",capability_id="AI-SYS-001",objective="Improve offer qualification evidence",mechanism="evidence_fusion_v1",evidence_refs=("E3-provider",),affected_boundaries=("offer_ingress","eligibility"),requested_actions=frozenset({"read_analysis"}),novelty_basis=("new cross-boundary provenance comparison",),reversibility="read_only",human_approval_required=True)
    data.update(overrides); return InnovationProposal(**data)
class AIInnovationLoopTests(SimpleTestCase):
    def test_new_safe_proposal_becomes_candidate(self): self.assertEqual(evaluate_innovation(proposal(),frozenset({"old_ranker"})).state,"candidate")
    def test_known_mechanism_is_not_called_new(self): self.assertIn("mechanism_already_known",evaluate_innovation(proposal(),frozenset({"evidence_fusion_v1"})).reasons)
    def test_forbidden_action_is_rejected(self): self.assertIn("forbidden_action_requested",evaluate_innovation(proposal(requested_actions=frozenset({"wallet_mutation"})),frozenset()).reasons)
    def test_missing_evidence_is_rejected(self): self.assertEqual(evaluate_innovation(proposal(evidence_refs=()),frozenset()).state,"quarantined")
    def test_non_reversible_is_rejected(self): self.assertEqual(evaluate_innovation(proposal(reversibility="irreversible"),frozenset()).state,"quarantined")
    def test_approval_is_required(self):
        d=evaluate_innovation(proposal(),frozenset())
        with self.assertRaisesRegex(InnovationGateError,"innovation_human_approval_required"): promote_innovation_candidate(d,False)
        self.assertEqual(promote_innovation_candidate(d,True).state,"approved_for_design_review")
    def test_digest_is_stable(self): self.assertEqual(evaluate_innovation(proposal(),frozenset()).proposal_digest,evaluate_innovation(proposal(),frozenset()).proposal_digest)