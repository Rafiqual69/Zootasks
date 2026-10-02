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
