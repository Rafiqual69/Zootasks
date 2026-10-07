from django.test import SimpleTestCase

from .ai_action_risk import AIRiskLevel
from .ai_control_plane import (
    AIProposal,
    AIGuardError,
    MAX_PLAN_STEPS,
    MAX_RETRIES_PER_STEP,
    evaluate_ai_plan,
    validate_ai_proposal,
    validate_retry_count,
)


class AIControlPlaneTests(SimpleTestCase):
    def proposal(self, **overrides):
        values = {
            "tool": "read_project_data",
            "action": "read_scoped_project_data",
            "target": "project:security",
            "scope": "read:security",
            "parameters": {"query": "migration status"},
        }
        values.update(overrides)
        return AIProposal(**values)

    def test_allowlisted_read_tool_is_low_risk(self):
        self.assertEqual(validate_ai_proposal(self.proposal()), AIRiskLevel.LOW)

    def test_unknown_tool_is_denied(self):
        with self.assertRaises(AIGuardError):
            validate_ai_proposal(self.proposal(tool="shell"))

    def test_tool_action_mismatch_is_denied(self):
        with self.assertRaises(AIGuardError):
            validate_ai_proposal(
                self.proposal(action="modify_wallet_balance")
            )

    def test_critical_action_cannot_enter_ai_tool_execution_path(self):
        with self.assertRaises(AIGuardError):
            validate_ai_proposal(
                self.proposal(
                    tool="send_external_message",
                    action="modify_wallet_balance",
                )
            )

    def test_plan_is_bounded_and_digest_is_deterministic(self):
        proposals = [self.proposal()]
        first = evaluate_ai_plan(
            proposals=proposals,
            request_id="req-001",
            environment="development",
            policy_version="1.0.0",
        )
        second = evaluate_ai_plan(
            proposals=proposals,
            request_id="req-001",
            environment="development",
            policy_version="1.0.0",
        )
        self.assertEqual(first.risk, AIRiskLevel.LOW)
        self.assertFalse(first.human_governance_required)
        self.assertEqual(first.request_digest, second.request_digest)

    def test_plan_step_limit_fails_closed(self):
        with self.assertRaises(AIGuardError):
            evaluate_ai_plan(
                proposals=[self.proposal() for _ in range(MAX_PLAN_STEPS + 1)],
                request_id="req-002",
                environment="development",
                policy_version="1.0.0",
            )

    def test_sensitive_parameter_is_rejected_by_request_binding(self):
        with self.assertRaises(AIGuardError):
            evaluate_ai_plan(
                proposals=[
                    self.proposal(parameters={"api_token": "should-never-bind"})
                ],
                request_id="req-003",
                environment="development",
                policy_version="1.0.0",
            )

    def test_retry_budget_is_bounded(self):
        validate_retry_count(MAX_RETRIES_PER_STEP - 1)
        with self.assertRaises(AIGuardError):
            validate_retry_count(MAX_RETRIES_PER_STEP)

    def test_high_impact_external_message_requires_separate_governed_path(self):
        with self.assertRaises(AIGuardError):
            evaluate_ai_plan(
                proposals=[
                    self.proposal(
                        tool="send_external_message",
                        action="send_external_message",
                    )
                ],
                request_id="req-004",
                environment="development",
                policy_version="1.0.0",
            )
