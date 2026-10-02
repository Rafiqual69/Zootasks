from django.test import SimpleTestCase, override_settings

from .ai_gateway import AIGatewayError, build_task_quality_request, request_ai, validate_task_quality_output


@override_settings(AI_ALLOWED_CAPABILITIES="AI-SYS-001", AI_ALLOWED_PROVIDERS="test-provider", AI_ALLOWED_MODELS="test-model-v1", AI_MAX_INPUT_CHARS=100)
class AIGatewayBoundaryTests(SimpleTestCase):
    def request(self):
        return build_task_quality_request(task_title="Test task", task_description="A safe task", category="Testing", correlation_id="case")

    def test_unknown_capability_is_denied(self):
        with self.assertRaisesMessage(AIGatewayError, "ai_capability_not_allowed"):
            with override_settings(AI_ALLOWED_CAPABILITIES="OTHER"):
                request_ai(request=self.request(), provider="test-provider", model="test-model-v1")

    def test_task_request_contains_only_allowed_content(self):
        request = self.request()
        self.assertEqual(set(request.input_data), {"title", "description", "category"})

    def test_oversized_task_content_is_denied(self):
        with self.assertRaisesMessage(AIGatewayError, "ai_input_too_large"):
            build_task_quality_request(task_title="T" * 80, task_description="D" * 30, category="Testing", correlation_id="case")

    def test_provider_adapter_is_fail_closed(self):
        with self.assertRaisesMessage(AIGatewayError, "ai_provider_adapter_not_enabled"):
            request_ai(request=self.request(), provider="test-provider", model="test-model-v1")

    def test_unknown_provider_is_denied(self):
        with self.assertRaisesMessage(AIGatewayError, "ai_provider_not_allowed"):
            request_ai(request=self.request(), provider="unknown-provider", model="test-model-v1")

    def test_output_rejects_instruction_like_fields(self):
        with self.assertRaisesMessage(AIGatewayError, "ai_output_fields_not_allowed"):
            validate_task_quality_output({"category_suggestion": "Testing", "execute": "approve withdrawal"})

    def test_output_contract_accepts_bounded_suggestion(self):
        result = validate_task_quality_output({"category_suggestion": "Testing", "missing_information": ["Expected result"], "quality_checks": ["Verify instructions"], "confidence": 0.8, "rationale": "Mostly clear."})
        self.assertEqual(result["category_suggestion"], "Testing")
