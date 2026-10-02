from django.test import SimpleTestCase, override_settings

from core.ai_evaluation_runner import run_evaluation


class AIEvaluationRunnerTests(SimpleTestCase):
    @override_settings(
        AI_ALLOWED_CAPABILITIES="task_quality_assistance",
        AI_ALLOWED_PROVIDERS="test",
        AI_ALLOWED_MODELS="test-model",
        AI_MAX_INPUT_CHARS=12000,
    )
    def test_runner_emits_machine_readable_pass_evidence(self):
        evidence = run_evaluation()

        self.assertEqual(evidence["evidence_type"], "zootasks.ai.security_evaluation")
        self.assertEqual(evidence["schema_version"], "1.0")
        self.assertEqual(evidence["system_id"], "AI-SYS-001")
        self.assertFalse(evidence["production_provider_invoked"])
        self.assertEqual(evidence["summary"]["status"], "PASS")
        self.assertEqual(evidence["summary"]["failed"], 0)
        self.assertGreaterEqual(evidence["summary"]["total"], 6)
        self.assertEqual(len(evidence["cases"]), evidence["summary"]["total"])
