from django.test import SimpleTestCase

from .ai_tool_permission import AIToolPermissionError, validate_tool_permission


class AIToolPermissionTests(SimpleTestCase):
    def test_current_agent_has_no_tools(self):
        with self.assertRaisesMessage(AIToolPermissionError, "ai_tool_not_allowed"):
            validate_tool_permission(
                agent_id="ZT-AGENT-001",
                capability_id="AI-SYS-001",
                tool_class="database_read",
            )

    def test_unknown_agent_is_denied(self):
        with self.assertRaisesMessage(AIToolPermissionError, "ai_tool_agent_not_allowed"):
            validate_tool_permission(
                agent_id="ZT-AGENT-999",
                capability_id="AI-SYS-001",
                tool_class="database_read",
            )

    def test_unknown_capability_is_denied(self):
        with self.assertRaisesMessage(AIToolPermissionError, "ai_tool_capability_not_allowed"):
            validate_tool_permission(
                agent_id="ZT-AGENT-001",
                capability_id="AI-SYS-999",
                tool_class="database_read",
            )

    def test_side_effects_are_denied(self):
        with self.assertRaisesMessage(AIToolPermissionError, "ai_tool_not_allowed"):
            validate_tool_permission(
                agent_id="ZT-AGENT-001",
                capability_id="AI-SYS-001",
                tool_class="external_api",
                external_side_effects=True,
            )
