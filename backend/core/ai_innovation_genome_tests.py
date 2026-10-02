from django.test import SimpleTestCase
from core.ai_innovation_genome import InnovationGenome, InnovationGenomeError, evaluate_genome, genome_fingerprint, novelty_distance

def genome(**overrides):
    data=dict(capability="offer discovery",workflow="quarantine then verify",integration="read-only provider boundary",safety="human approval plus fail-closed",worker_value="better legitimate task matching")
    data.update(overrides); return InnovationGenome(**data)

class AIInnovationGenomeTests(SimpleTestCase):
    def test_fingerprint_is_deterministic(self):
        self.assertEqual(genome_fingerprint(genome()),genome_fingerprint(genome()))
    def test_exact_genome_is_known(self):
        state,reasons=evaluate_genome(genome(),(genome(),))
        self.assertEqual(state,"known")
        self.assertIn("exact_genome_match",reasons)
    def test_changed_dimension_is_novel_candidate(self):
        candidate=genome(integration="provider federation with signed source revisions")
        state,reasons=evaluate_genome(candidate,(genome(),))
        self.assertEqual(state,"novel_candidate")
        self.assertIn("changed_dimensions:1",reasons)
    def test_multiple_dimensions_are_detected(self):
        candidate=genome(workflow="continuous staged qualification",safety="reversible sandbox and circuit breaker")
        self.assertEqual(novelty_distance(candidate,(genome(),)),2)
    def test_empty_dimension_is_rejected(self):
        with self.assertRaisesRegex(InnovationGenomeError,"all_genome_dimensions_required"):
            genome(capability="")


from core.ai_mechanism_catalog import MechanismRecord, evaluate_against_catalog, catalog_fingerprint
from core.ai_provenance_queue import enqueue_observation, content_digest, observation_digest

class MechanismCatalogAndProvenanceTests(SimpleTestCase):
    def test_exact_mechanism_is_known(self):
        g=genome(); r=MechanismRecord("MECH-001","Provider federation",g,("E1",))
        d=evaluate_against_catalog(g,[r])
        self.assertEqual(d.state,"known"); self.assertEqual(d.matched_mechanism_id,"MECH-001")
    def test_changed_mechanism_is_candidate(self):
        g=genome(); r=MechanismRecord("MECH-001","Provider federation",g)
        d=evaluate_against_catalog(genome(integration="signed provider federation"),[r])
        self.assertEqual(d.state,"candidate")
    def test_catalog_order_does_not_change_fingerprint(self):
        a=MechanismRecord("A","A",genome()); b=MechanismRecord("B","B",genome(workflow="other"))
        self.assertEqual(catalog_fingerprint([a,b]),catalog_fingerprint([b,a]))
    def test_provenance_is_quarantined_and_stable(self):
        kw=dict(observation_id="OBS-1",source_kind="url",source_identifier="source-1",observed_at="2026-10-02T18:00:00+00:00",payload={"x":1},sequence=1)
        a=enqueue_observation(**kw); b=enqueue_observation(**kw)
        self.assertEqual(a.status,"quarantined"); self.assertEqual(a.record_digest,b.record_digest); self.assertEqual(a.record.trust_state,"untrusted")
    def test_provenance_payload_and_chain_are_digest_bound(self):
        self.assertNotEqual(content_digest({"x":1}),content_digest({"x":2}))
        a=enqueue_observation(observation_id="OBS-2",source_kind="api",source_identifier="p",observed_at="2026-10-02T18:00:00+00:00",payload={"x":1})
        b=enqueue_observation(observation_id="OBS-2",source_kind="api",source_identifier="p",observed_at="2026-10-02T18:00:00+00:00",payload={"x":1},previous_digest="a"*64)
        self.assertNotEqual(observation_digest(a.record),observation_digest(b.record))


from core.ai_agent_card import parse_agent_card, card_digest, is_signed
from core.ai_delegation_token import Delegation, delegation_digest, authorize_delegated_call

class AgentCardDelegationTests(SimpleTestCase):
    def test_card_normalization_and_digest_are_deterministic(self):
        payload={"agent_id":"A1","provider_id":"P1","version":"1","protocols":["a2a"],"capabilities":["research"],"destinations":["research"]}
        a=parse_agent_card(payload); b=parse_agent_card(payload)
        self.assertEqual(card_digest(a),card_digest(b)); self.assertFalse(is_signed(a))
    def test_delegation_is_scoped_and_bounded(self):
        d=Delegation("D1","A1","A2",("research",),("approved_research",),("research",),3,"2026-10-03T00:00:00+00:00")
        self.assertTrue(authorize_delegated_call(d,action="research",tool="approved_research",destination="research",calls_used=0))
        self.assertEqual(len(delegation_digest(d)),64)
    def test_delegation_cannot_include_financial_authority(self):
        d=Delegation("D2","A1","A2",("wallet_mutation",),("approved",),(),1,"2026-10-03T00:00:00+00:00")
        with self.assertRaises(ValueError): delegation_digest(d)


from core.ai_source_attestation import SourceManifest, evaluate_manifest
from core.ai_privacy_gate import PrivacyPolicy, evaluate_privacy

class SourcePrivacyGateTests(SimpleTestCase):
    def test_unverified_source_is_quarantined(self):
        m=SourceManifest("S1","P1","1","provider",("BD",),("E1",))
        self.assertEqual(evaluate_manifest(m).state,"quarantined")
    def test_attested_source_is_only_a_candidate(self):
        m=SourceManifest("S1","P1","1","provider",("BD",),("E1",),"ATT-1","attested")
        self.assertEqual(evaluate_manifest(m).state,"candidate")
    def test_privacy_requires_explicit_approval(self):
        p=PrivacyPolicy("personal","task evaluation","30 days",("no resale",),("BD",),False)
        self.assertEqual(evaluate_privacy(p,region="BD").state,"quarantined")
    def test_unapproved_region_is_quarantined(self):
        p=PrivacyPolicy("public","evaluation","7 days",(),("US",),True)
        self.assertEqual(evaluate_privacy(p,region="BD").state,"quarantined")


from core.ai_delegation_chain import ChainLink, DelegationChainError, verify_chain

class DelegationChainTests(SimpleTestCase):
    def test_valid_chain_is_deterministically_verified(self):
        root=ChainLink("D1","owner","exec",("research",),("approved_research",),("internal",),10)
        child=ChainLink("D2","exec","researcher",("research",),("approved_research",),("internal",),5,verify_chain((root,)))
        digest=verify_chain((root,child))
        self.assertTrue(digest)
        self.assertEqual(digest,verify_chain((root,child)))

    def test_parent_digest_mismatch_rejected(self):
        root=ChainLink("D1","owner","exec",("research",),("approved_research",),("internal",),10)
        child=ChainLink("D2","exec","researcher",("research",),("approved_research",),("internal",),5,"bad")
        with self.assertRaisesRegex(DelegationChainError,"delegation_parent_mismatch"):
            verify_chain((root,child))

    def test_action_escalation_rejected(self):
        root=ChainLink("D1","owner","exec",("research",),("approved_research",),("internal",),10)
        child=ChainLink("D2","exec","researcher",("external_side_effect",),("approved_research",),("internal",),5,verify_chain((root,)))
        with self.assertRaisesRegex(DelegationChainError,"delegation_action_escalation"):
            verify_chain((root,child))

    def test_budget_escalation_rejected(self):
        root=ChainLink("D1","owner","exec",("research",),("approved_research",),("internal",),5)
        child=ChainLink("D2","exec","researcher",("research",),("approved_research",),("internal",),6,verify_chain((root,)))
        with self.assertRaisesRegex(DelegationChainError,"delegation_budget_escalation"):
            verify_chain((root,child))


from core.ai_audit_ledger import AuditEntry, AuditLedgerError, entry_digest, verify_ledger

class AuditLedgerTests(SimpleTestCase):
    def _entry(self, sequence, previous=None):
        return AuditEntry(sequence, f"E{sequence}", "agent-1", "read_analysis", "auth", "source", "input", "result", "2026-10-02T00:00:00Z", previous)

    def test_hash_chained_ledger_verifies(self):
        first=self._entry(0)
        second=self._entry(1,entry_digest(first))
        digest=verify_ledger((first,second))
        self.assertEqual(digest,entry_digest(second))

    def test_chain_break_rejected(self):
        first=self._entry(0)
        second=self._entry(1,"tampered")
        with self.assertRaisesRegex(AuditLedgerError,"audit_chain_break"):
            verify_ledger((first,second))

    def test_sequence_tampering_rejected(self):
        first=self._entry(1)
        with self.assertRaisesRegex(AuditLedgerError,"audit_sequence_invalid"):
            verify_ledger((first,))


from core.ai_policy_evidence_bundle import PolicyEvidenceBundle, PolicyEvidenceError, bundle_digest, verify_bundle

class PolicyEvidenceBundleTests(SimpleTestCase):
    def _bundle(self, decision="review", approval=None):
        return PolicyEvidenceBundle("B1","policy-v1","auth","delegation","source","privacy","audit",decision,approval)

    def test_bundle_digest_is_deterministic(self):
        b=self._bundle()
        self.assertEqual(bundle_digest(b),bundle_digest(b))

    def test_allow_requires_approval_reference(self):
        with self.assertRaisesRegex(PolicyEvidenceError,"allow_requires_approval_reference"):
            bundle_digest(self._bundle("allow"))

    def test_tampered_bundle_fails_verification(self):
        b=self._bundle()
        digest=bundle_digest(b)
        tampered=PolicyEvidenceBundle("B1","policy-v2","auth","delegation","source","privacy","audit","review")
        with self.assertRaisesRegex(PolicyEvidenceError,"evidence_bundle_digest_mismatch"):
            verify_bundle(tampered,digest)

    def test_approved_bundle_verifies(self):
        b=self._bundle("allow","OWNER-APPROVAL-1")
        self.assertTrue(verify_bundle(b,bundle_digest(b)))


from core.ai_release_tevv_gate import ReleaseEvidence, ReleaseGateError, evaluate_release, release_digest

class ReleaseTEVVGateTests(SimpleTestCase):
    def _release(self, state="candidate", approval=None):
        return ReleaseEvidence("R1","AI-SYS-001","git-1","src-1","eval-1","policy-1","test-1","rollback-1","monitor-1",approval,state)

    def test_candidate_is_quarantined(self):
        state,digest=evaluate_release(self._release())
        self.assertEqual(state,"quarantined")
        self.assertEqual(digest,release_digest(self._release()))

    def test_approved_release_requires_approval(self):
        with self.assertRaisesRegex(ReleaseGateError,"release_approval_required"):
            release_digest(self._release("approved"))

    def test_approved_release_reaches_controlled_rollout(self):
        state,_=evaluate_release(self._release("approved","OWNER-APPROVAL-1"))
        self.assertEqual(state,"approved_for_controlled_rollout")

    def test_missing_monitoring_evidence_rejected(self):
        bad=ReleaseEvidence("R1","AI-SYS-001","git-1","src-1","eval-1","policy-1","test-1","rollback-1","","OWNER-APPROVAL-1","approved")
        with self.assertRaisesRegex(ReleaseGateError,"release_evidence_required"):
            release_digest(bad)


from core.ai_runtime_monitor import RuntimePolicy, RuntimeObservation, RuntimeMonitorError, runtime_decision, enforce_runtime_gate

class RuntimeTrustSentinelTests(SimpleTestCase):
    def _obs(self, **kw):
        data=dict(system_id="AI-SYS-001", release_id="R1", calls=100, failures=1, consecutive_failures=0, latency_ms=1000, drift_score=5)
        data.update(kw)
        return RuntimeObservation(**data)

    def test_healthy_runtime_continues(self):
        d=runtime_decision(RuntimePolicy(), self._obs())
        self.assertEqual(d.state, "healthy")
        self.assertFalse(d.rollback_required)
        self.assertEqual(enforce_runtime_gate(RuntimePolicy(), self._obs()), "healthy")

    def test_error_rate_requires_quarantine(self):
        d=runtime_decision(RuntimePolicy(), self._obs(failures=10))
        self.assertIn("error_rate_exceeded", d.reasons)
        self.assertTrue(d.rollback_required)
        self.assertEqual(enforce_runtime_gate(RuntimePolicy(), self._obs(failures=10)), "quarantined")

    def test_policy_violation_requires_quarantine(self):
        d=runtime_decision(RuntimePolicy(), self._obs(policy_violations=1))
        self.assertEqual(d.state, "rollback_required")

    def test_invalid_observation_fails_closed(self):
        with self.assertRaisesRegex(RuntimeMonitorError, "failures_exceed_calls"):
            runtime_decision(RuntimePolicy(), self._obs(calls=1, failures=2))

    def test_decision_digest_is_stable(self):
        a=runtime_decision(RuntimePolicy(), self._obs())
        b=runtime_decision(RuntimePolicy(), self._obs())
        self.assertEqual(a.decision_digest, b.decision_digest)


from core.ai_incident_response import IncidentEvidence, IncidentResponseError, incident_digest, transition_incident

class IncidentResponseStateMachineTests(SimpleTestCase):
    def _incident(self, **kw):
        data=dict(
            incident_id="INC-1",
            system_id="AI-SYS-001",
            release_id="R1",
            severity="high",
            detection_reason="error_rate_exceeded",
            runtime_decision_digest="d"*64,
        )
        data.update(kw)
        return IncidentEvidence(**data)

    def test_detection_quarantine_and_rollback_path_is_ordered(self):
        incident=transition_incident(self._incident(), "quarantined")
        incident=transition_incident(incident, "rollback_candidate")
        incident=transition_incident(incident, "rollback_approved", approval_ref="OWNER-APPROVAL-1")
        incident=transition_incident(incident, "rolled_back", rollback_ref="ROLLBACK-R1")
        incident=transition_incident(incident, "revalidation_required")
        recovered=transition_incident(incident, "recovered", revalidation_ref="TEVV-R1")
        self.assertEqual(recovered.state, "recovered")

    def test_invalid_transition_fails_closed(self):
        with self.assertRaisesRegex(IncidentResponseError, "incident_transition_denied"):
            transition_incident(self._incident(), "rolled_back")

    def test_rollback_requires_approval_and_reference(self):
        incident=transition_incident(self._incident(), "quarantined")
        incident=transition_incident(incident, "rollback_candidate")
        with self.assertRaisesRegex(IncidentResponseError, "incident_approval_required"):
            transition_incident(incident, "rollback_approved")
        incident=transition_incident(incident, "rollback_approved", approval_ref="OWNER-APPROVAL-1")
        with self.assertRaisesRegex(IncidentResponseError, "rollback_reference_required"):
            transition_incident(incident, "rolled_back")

    def test_recovery_requires_revalidation(self):
        incident=transition_incident(self._incident(), "quarantined")
        incident=transition_incident(incident, "rollback_candidate")
        incident=transition_incident(incident, "rollback_approved", approval_ref="OWNER-APPROVAL-1")
        incident=transition_incident(incident, "rolled_back", rollback_ref="ROLLBACK-R1")
        incident=transition_incident(incident, "revalidation_required")
        with self.assertRaisesRegex(IncidentResponseError, "revalidation_reference_required"):
            transition_incident(incident, "recovered")

    def test_terminal_state_cannot_be_reopened(self):
        incident=transition_incident(self._incident(), "quarantined")
        incident=transition_incident(incident, "decommissioned", approval_ref="OWNER-APPROVAL-1")
        with self.assertRaisesRegex(IncidentResponseError, "incident_terminal_state"):
            transition_incident(incident, "quarantined")

    def test_incident_digest_is_deterministic(self):
        incident=self._incident()
        self.assertEqual(incident_digest(incident), incident_digest(incident))


from core.ai_incident_evidence_binding import IncidentEvidenceBindingError, bind_incident_evidence

class IncidentEvidenceBindingTests(SimpleTestCase):
    def _runtime(self, system_id="AI-SYS-001", release_id="R1"):
        return runtime_decision(
            RuntimePolicy(),
            RuntimeObservation(
                system_id=system_id, release_id=release_id,
                calls=100, failures=10, consecutive_failures=0,
                latency_ms=1000, drift_score=5,
            ),
        )

    def _incident(self):
        return IncidentEvidence(
            "INC-B1","AI-SYS-001","R1","high",
            "policy_violation_detected",self._runtime().decision_digest
        )

    def _policy(self):
        return PolicyEvidenceBundle(
            "B1","policy-v1","auth","delegation","source","privacy","audit","quarantine"
        )

    def _release(self):
        return ReleaseEvidence(
            "R1","AI-SYS-001","git-1","src-1","eval-1",
            "policy-1","test-1","rollback-1","monitor-1"
        )

    def test_incident_binding_is_deterministic(self):
        incident=self._incident()
        policy=self._policy()
        release=self._release()
        binding=bind_incident_evidence(
            incident,policy,release,self._runtime(),
            expected_incident_digest=incident_digest(incident),
            expected_policy_bundle_digest=bundle_digest(policy),
            expected_release_digest=release_digest(release),
        )
        self.assertEqual(binding.binding_digest, bind_incident_evidence(
            incident,policy,release,
            expected_incident_digest=incident_digest(incident),
            expected_policy_bundle_digest=bundle_digest(policy),
            expected_release_digest=release_digest(release),
        ).binding_digest)

    def test_identity_mismatch_fails_closed(self):
        incident=IncidentEvidence(
            "INC-B2","OTHER-SYS","R1","high",
            "policy_violation_detected","d"*64
        )
        policy=self._policy()
        release=self._release()
        with self.assertRaisesRegex(IncidentEvidenceBindingError, "incident_release_identity_mismatch"):
            bind_incident_evidence(
                incident,policy,release,
                expected_incident_digest=incident_digest(incident),
                expected_policy_bundle_digest=bundle_digest(policy),
                expected_release_digest=release_digest(release),
            )

    def test_allow_bundle_cannot_be_used_as_incident_evidence(self):
        incident=self._incident()
        policy=PolicyEvidenceBundle(
            "B2","policy-v1","auth","delegation","source","privacy","audit",
            "allow","OWNER-APPROVAL-1"
        )
        release=self._release()
        with self.assertRaisesRegex(IncidentEvidenceBindingError, "incident_binding_allow_bundle_forbidden"):
            bind_incident_evidence(
                incident,policy,release,
                expected_incident_digest=incident_digest(incident),
                expected_policy_bundle_digest=bundle_digest(policy),
                expected_release_digest=release_digest(release),
            )

    def test_runtime_decision_digest_format_is_fail_closed(self):
        incident=IncidentEvidence(
            "INC-B3","AI-SYS-001","R1","high",
            "policy_violation_detected","not-a-sha256"
        )
        policy=self._policy()
        release=self._release()
        with self.assertRaisesRegex(IncidentEvidenceBindingError, "runtime_decision_digest_invalid"):
            bind_incident_evidence(
                incident,policy,release,
                expected_incident_digest=incident_digest(incident),
                expected_policy_bundle_digest=bundle_digest(policy),
                expected_release_digest=release_digest(release),
            )
