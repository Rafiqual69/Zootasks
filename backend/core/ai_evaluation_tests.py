from django.test import SimpleTestCase, override_settings

from .ai_evaluation_cases import CASES, EVALUATION_DATASET_VERSION
from .ai_gateway import AIGatewayError, build_task_quality_request, validate_task_quality_output


class AIEvaluationDatasetTests(SimpleTestCase):
    def test_dataset_is_versioned_and_synthetic(self):
        self.assertTrue(EVALUATION_DATASET_VERSION.startswith("AI-SYS-001-eval-"))
        self.assertGreaterEqual(len(CASES), 6)
        for case in CASES:
            self.assertIn("id", case)
            self.assertIn("group", case)
            self.assertIn("expected", case)

    def test_forbidden_financial_and_secret_inputs_are_not_gateway_fields(self):
        request = build_task_quality_request(
            task_title="Classify this task",
            task_description=CASES[1]["input"],
            category="Testing",
            correlation_id="eval-financial",
        )
        self.assertEqual(
            set(request.input_data),
            {"title", "description", "category"},
        )

    def test_malformed_executable_output_is_rejected(self):
        with self.assertRaisesMessage(AIGatewayError, "ai_output_fields_not_allowed"):
            validate_task_quality_output(
                {
                    "category_suggestion": "Testing",
                    "action": {"type": "approve_withdrawal"},
                }
            )

    def test_output_values_are_bounded(self):
        with self.assertRaisesMessage(AIGatewayError, "ai_output_rationale_invalid"):
            validate_task_quality_output(
                {
                    "category_suggestion": "Testing",
                    "rationale": "x" * 1001,
                }
            )

    def test_confidence_cannot_escape_unit_interval(self):
        with self.assertRaisesMessage(AIGatewayError, "ai_output_confidence_invalid"):
            validate_task_quality_output(
                {
                    "category_suggestion": "Testing",
                    "confidence": 1.01,
                }
            )
