from django.test import SimpleTestCase, override_settings

from core.ai_evaluation_integrity import evidence_sha256, sha256_json
from core.ai_evaluation_runner import run_evaluation


class AIEvaluationIntegrityTests(SimpleTestCase):
    @override_settings(
        AI_ALLOWED_CAPABILITIES="AI-SYS-001",
        AI_ALLOWED_PROVIDERS="test-provider",
        AI_ALLOWED_MODELS="test-model-v1",
        AI_MAX_INPUT_CHARS=12000,
    )
    def test_evidence_contains_provenance_and_self_consistent_digest(self):
        evidence = run_evaluation()

        self.assertEqual(evidence["provenance"]["git_commit"] != "", True)
        self.assertEqual(evidence["provenance"]["dataset_sha256"], sha256_json(
            __import__("core.ai_evaluation_cases", fromlist=["CASES"]).CASES
        ))
        self.assertEqual(
            evidence["integrity"]["evidence_sha256"],
            evidence_sha256(evidence),
        )

    def test_integrity_digest_excludes_only_integrity_container(self):
        evidence = {"system_id": "AI-SYS-001", "summary": {"status": "PASS"}}
        first = evidence_sha256(evidence)
        evidence["integrity"] = {"algorithm": "sha256", "evidence_sha256": first}
        self.assertEqual(first, evidence_sha256(evidence))
