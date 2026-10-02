from django.test import SimpleTestCase

from .ai_capability_budget import (
    AICapabilityBudgetError,
    validate_execution_budget,
    validate_input_budget,
    validate_output_budget,
)


class AICapabilityBudgetTests(SimpleTestCase):
    def test_unknown_capability_has_no_budget(self):
        with self.assertRaisesMessage(AICapabilityBudgetError, "ai_capability_budget_not_found"):
            validate_input_budget(capability_id="AI-SYS-999", input_data={})

    def test_input_budget_is_enforced(self):
        with self.assertRaisesMessage(AICapabilityBudgetError, "ai_input_budget_exceeded"):
            validate_input_budget(
                capability_id="AI-SYS-001",
                input_data={"description": "x" * 12001},
            )

    def test_output_budget_is_enforced(self):
        with self.assertRaisesMessage(AICapabilityBudgetError, "ai_output_budget_exceeded"):
            validate_output_budget(
                capability_id="AI-SYS-001",
                output={"rationale": "x" * 3001},
            )

    def test_output_list_budget_is_enforced(self):
        with self.assertRaisesMessage(AICapabilityBudgetError, "ai_output_list_budget_exceeded"):
            validate_output_budget(
                capability_id="AI-SYS-001",
                output={"quality_checks": ["x"] * 11},
            )

    def test_tool_calls_are_forbidden(self):
        with self.assertRaisesMessage(AICapabilityBudgetError, "ai_tool_budget_exceeded"):
            validate_execution_budget(
                capability_id="AI-SYS-001",
                tool_calls=1,
                external_side_effects=False,
            )

    def test_external_side_effects_are_forbidden(self):
        with self.assertRaisesMessage(AICapabilityBudgetError, "ai_external_side_effect_forbidden"):
            validate_execution_budget(
                capability_id="AI-SYS-001",
                tool_calls=0,
                external_side_effects=True,
            )
