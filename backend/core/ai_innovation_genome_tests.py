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
