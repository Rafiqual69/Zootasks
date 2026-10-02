from django.test import SimpleTestCase

from core.ai_agent_capability_gate import (
    AgentCapability,
    AgentCapabilityError,
    AgentCapabilityRequest,
    authorize_capability,
    registered_capabilities,
)


class AIAgentCapabilityGateTests(SimpleTestCase):
    def test_registered_capabilities_are_fail_closed_for_side_effects(self):
        for capability in registered_capabilities():
            self.assertEqual(capability.max_external_side_effects, 0)
            self.assertTrue(
                capability.allowed_actions.isdisjoint(
                    {
                        "wallet_mutation",
                        "withdrawal_approval",
                        "withdrawal_payment",
                        "promotion_payout",
                        "permission_change",
                    }
                )
            )

    def test_unknown_action_is_rejected(self):
        capability = registered_capabilities()[0]
        with self.assertRaisesRegex(AgentCapabilityError, "agent_action_not_allowed"):
            authorize_capability(
                capability,
                AgentCapabilityRequest(
                    agent_id=capability.agent_id,
                    capability_id=capability.capability_id,
                    action="send_money",
                ),
            )

    def test_financial_action_is_forbidden_even_if_added_to_allowlist(self):
        capability = AgentCapability(
            capability_id="TEST-001",
            agent_id="test-agent",
            allowed_actions=frozenset({"wallet_mutation"}),
        )
        with self.assertRaisesRegex(AgentCapabilityError, "agent_action_forbidden"):
            authorize_capability(
                capability,
                AgentCapabilityRequest(
                    agent_id="test-agent",
                    capability_id="TEST-001",
                    action="wallet_mutation",
                ),
            )

    def test_acquisition_external_action_requires_human_approval(self):
        capability = registered_capabilities()[1]
        request = AgentCapabilityRequest(
            agent_id=capability.agent_id,
            capability_id=capability.capability_id,
            action="draft_outreach",
        )
        with self.assertRaisesRegex(AgentCapabilityError, "agent_human_approval_required"):
            authorize_capability(capability, request)

        authorize_capability(capability, request.__class__(**{**request.__dict__, "approved": True}))

    def test_tool_budget_is_enforced(self):
        capability = registered_capabilities()[0]
        with self.assertRaisesRegex(AgentCapabilityError, "agent_tool_budget_exceeded"):
            authorize_capability(
                capability,
                AgentCapabilityRequest(
                    agent_id=capability.agent_id,
                    capability_id=capability.capability_id,
                    action="read_analysis",
                    tool_calls_used=capability.max_tool_calls + 1,
                ),
            )

    def test_side_effect_budget_is_always_zero_for_registered_agents(self):
        capability = registered_capabilities()[0]
        with self.assertRaisesRegex(AgentCapabilityError, "agent_side_effect_budget_exceeded"):
            authorize_capability(
                capability,
                AgentCapabilityRequest(
                    agent_id=capability.agent_id,
                    capability_id=capability.capability_id,
                    action="read_analysis",
                    external_side_effects_used=1,
                ),
            )

    def test_negative_budget_counters_are_rejected(self):
        capability = registered_capabilities()[0]
        with self.assertRaisesRegex(AgentCapabilityError, "agent_tool_budget_invalid"):
            authorize_capability(
                capability,
                AgentCapabilityRequest(
                    agent_id=capability.agent_id,
                    capability_id=capability.capability_id,
                    action="read_analysis",
                    tool_calls_used=-1,
                ),
            )

    def test_unapproved_tool_and_destination_are_rejected(self):
        capability = registered_capabilities()[0]
        with self.assertRaisesRegex(AgentCapabilityError, "agent_tool_not_allowed"):
            authorize_capability(
                capability,
                AgentCapabilityRequest(
                    agent_id=capability.agent_id,
                    capability_id=capability.capability_id,
                    action="read_analysis",
                    tool="arbitrary_shell",
                ),
            )
