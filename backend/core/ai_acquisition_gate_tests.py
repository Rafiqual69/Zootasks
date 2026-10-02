from datetime import datetime, timezone
from django.test import SimpleTestCase
from core.ai_acquisition_gate import AcquisitionApproval, AcquisitionGateError, AcquisitionProposal, authorize_transition, proposal_digest

def proposal(**kw):
    d=dict(proposal_id="P1",provider_id="provider-a",purpose="authorized partnership inquiry",channel="approved_business_email",material_parameters=(("region","global"),("task_type","evaluation")),evidence_refs=("e1",),state="draft_ready")
    d.update(kw); return AcquisitionProposal(**d)

class AIAcquisitionGateTests(SimpleTestCase):
    def test_normal_transition_is_allowed(self): self.assertEqual(authorize_transition(proposal(),"awaiting_owner_approval").state,"awaiting_owner_approval")
    def test_external_transition_requires_approval(self):
        with self.assertRaisesRegex(AcquisitionGateError,"external_action_approval_required"): authorize_transition(proposal(),"sent")
    def test_approval_binds_exact_digest(self):
        a=AcquisitionApproval(proposal_digest(proposal()),"owner","provider-a","2030-01-01T00:00:00Z")
        with self.assertRaisesRegex(AcquisitionGateError,"approval_proposal_digest_mismatch"): authorize_transition(proposal(region="BD"),"sent",a,datetime(2029,1,1,tzinfo=timezone.utc))
    def test_expired_approval_rejected(self):
        a=AcquisitionApproval(proposal_digest(proposal()),"owner","provider-a","2020-01-01T00:00:00Z")
        with self.assertRaisesRegex(AcquisitionGateError,"approval_expired"): authorize_transition(proposal(),"sent",a,datetime(2026,1,1,tzinfo=timezone.utc))
    def test_quarantine_is_terminal(self):
        with self.assertRaisesRegex(AcquisitionGateError,"terminal_state"): authorize_transition(proposal(state="quarantined"),"draft_ready")
