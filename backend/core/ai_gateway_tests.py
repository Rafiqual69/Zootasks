from django.test import SimpleTestCase, override_settings

from .ai_agent_session import issue_agent_session
from .ai_gateway import AIGatewayError, build_task_quality_request, request_ai, validate_task_quality_output


@override_settings(AI_ALLOWED_CAPABILITIES="AI-SYS-001", AI_ALLOWED_PROVIDERS="test-provider", AI_ALLOWED_MODELS="test-model-v1", AI_MAX_INPUT_CHARS=100)
class AIGatewayBoundaryTests(SimpleTestCase):
    def request(self):
        return build_task_quality_request(task_title="Test task", task_description="A safe task", category="Testing", correlation_id="case")

    def test_agent_authorization_binds_session_and_provenance(self):
        from .ai_gateway import authorize_agent_request
        request = self.request()
        session = issue_agent_session(
            session_id="sess-test",
            agent_id="ZT-AGENT-001",
            audience="zootasks-ai-gateway",
            scopes=frozenset({"task_quality:suggest"}),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )
        receipt = authorize_agent_request(request=request, session=session)
        self.assertEqual(receipt["decision"], "authorized")
        self.assertEqual(receipt["agent_id"], "ZT-AGENT-001")

    def test_wrong_session_is_rejected(self):
        from .ai_gateway import authorize_agent_request, AIGatewayError
        request = self.request()
        session = issue_agent_session(
            session_id="sess-test",
            agent_id="ZT-AGENT-999",
            audience="zootasks-ai-gateway",
            scopes=frozenset({"task_quality:suggest"}),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )
        with self.assertRaisesMessage(AIGatewayError, "ai_agent_authorization_rejected"):
            authorize_agent_request(request=request, session=session)

    def test_tool_execution_is_fail_closed(self):
        request = self.request()
        with self.assertRaisesMessage(AIGatewayError, "ai_tool_not_allowed"):
            from .ai_gateway import validate_tool_execution
            validate_tool_execution(request=request, tool_class="database_read")

    def test_registered_agent_is_bound_to_request(self):
        request = self.request()
        self.assertEqual(request.agent_id, "ZT-AGENT-001")
        self.assertEqual(request.capability_id, "AI-SYS-001")

    def test_unknown_agent_is_denied(self):
        with self.assertRaisesMessage(AIGatewayError, "ai_agent_policy_rejected"):
            build_task_quality_request(
                task_title="Test task",
                task_description="A safe task",
                category="Testing",
                correlation_id="case",
                agent_id="ZT-AGENT-999",
            )

    def test_unknown_capability_is_denied(self):
        with self.assertRaisesMessage(AIGatewayError, "ai_capability_not_allowed"):
            with override_settings(AI_ALLOWED_CAPABILITIES="OTHER"):
                request_ai(request=self.request(), provider="test-provider", model="test-model-v1")

    def test_task_request_contains_only_allowed_content(self):
        request = self.request()
        self.assertEqual(set(request.input_data), {"title", "description", "category"})

    def test_task_request_redacts_sensitive_values(self):
        request = build_task_quality_request(
            task_title="Test task",
            task_description="Contact worker@example.com with api_key=SECRET123",
            category="Testing",
            correlation_id="case",
        )
        self.assertNotIn("worker@example.com", request.input_data["description"])
        self.assertNotIn("SECRET123", request.input_data["description"])

    def test_oversized_task_content_is_denied(self):
        with self.assertRaisesMessage(AIGatewayError, "ai_input_too_large"):
            build_task_quality_request(task_title="T" * 80, task_description="D" * 30, category="Testing", correlation_id="case")

    def test_production_approval_is_required(self):
        with self.assertRaisesMessage(AIGatewayError, "ai_production_not_approved"):
            request_ai(request=self.request(), provider="test-provider", model="test-model-v1")

    def test_approval_reference_is_required(self):
        with self.assertRaisesMessage(AIGatewayError, "ai_approval_reference_required"):
            with override_settings(AI_PRODUCTION_APPROVED=True, AI_APPROVAL_REFERENCE=""):
                request_ai(request=self.request(), provider="test-provider", model="test-model-v1")

    def test_provider_adapter_remains_fail_closed_after_approval(self):
        with self.assertRaisesMessage(AIGatewayError, "ai_provider_adapter_not_enabled"):
            with override_settings(AI_PRODUCTION_APPROVED=True, AI_APPROVAL_REFERENCE="TEST-APPROVAL"):
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
