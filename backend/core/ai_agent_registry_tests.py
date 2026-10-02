from django.test import SimpleTestCase

from .ai_agent_registry import (
    AIAgentRegistryError,
    get_agent_policy,
    validate_agent_autonomy,
    validate_agent_capability,
    validate_agent_data_class,
    validate_agent_tool,
)


class AIAgentRegistryTests(SimpleTestCase):
    def test_registered_agent_has_least_privilege_policy(self):
        policy = get_agent_policy("ZT-AGENT-001")
        self.assertEqual(policy.capability_ids, frozenset({"AI-SYS-001"}))
        self.assertEqual(policy.allowed_data_classes, frozenset({"task_content_minimal"}))
        self.assertEqual(policy.allowed_tool_classes, frozenset())
        self.assertEqual(policy.max_autonomy, "suggestion_only")

    def test_unknown_agent_is_rejected(self):
        with self.assertRaisesRegex(AIAgentRegistryError, "ai_agent_not_registered"):
            get_agent_policy("ZT-AGENT-999")

    def test_capability_is_explicitly_allowlisted(self):
        validate_agent_capability(agent_id="ZT-AGENT-001", capability_id="AI-SYS-001")
        with self.assertRaisesRegex(AIAgentRegistryError, "ai_agent_capability_not_allowed"):
            validate_agent_capability(agent_id="ZT-AGENT-001", capability_id="AI-SYS-002")

    def test_sensitive_data_class_is_rejected(self):
        validate_agent_data_class(agent_id="ZT-AGENT-001", data_class="task_content_minimal")
        with self.assertRaisesRegex(AIAgentRegistryError, "ai_agent_data_class_not_allowed"):
            validate_agent_data_class(agent_id="ZT-AGENT-001", data_class="wallet_financial")

    def test_tools_are_deny_by_default(self):
        with self.assertRaisesRegex(AIAgentRegistryError, "ai_agent_tool_not_allowed"):
            validate_agent_tool(agent_id="ZT-AGENT-001", tool_class="database_write")

    def test_autonomy_cannot_be_escalated(self):
        validate_agent_autonomy(agent_id="ZT-AGENT-001", autonomy="suggestion_only")
        with self.assertRaisesRegex(AIAgentRegistryError, "ai_agent_autonomy_not_allowed"):
            validate_agent_autonomy(agent_id="ZT-AGENT-001", autonomy="autonomous")