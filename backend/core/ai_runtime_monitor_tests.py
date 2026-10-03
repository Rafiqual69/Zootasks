from django.test import SimpleTestCase

from core.ai_runtime_monitor import (
    RuntimeMonitorError,
    RuntimeObservation,
    RuntimePolicy,
    enforce_runtime_gate,
    runtime_decision,
    verify_runtime_decision_context,
)


class AIRuntimeMonitorTests(SimpleTestCase):
    def test_healthy_runtime_remains_healthy(self):
        policy = RuntimePolicy()
        observation = RuntimeObservation("AI-SYS-001", "release-1", 100, 1, 0, 100, 5)
        decision = runtime_decision(policy, observation)
        self.assertEqual(decision.state, "healthy")
        self.assertFalse(decision.rollback_required)
        self.assertEqual(enforce_runtime_gate(policy, observation), "healthy")
        self.assertTrue(verify_runtime_decision_context("AI-SYS-001", "release-1", decision))

    def test_policy_violation_requires_rollback(self):
        policy = RuntimePolicy(max_error_rate_pct=5)
        observation = RuntimeObservation("AI-SYS-001", "release-1", 10, 2, 0, 100, 5)
        decision = runtime_decision(policy, observation)
        self.assertEqual(decision.state, "rollback_required")
        self.assertTrue(decision.rollback_required)
        self.assertEqual(enforce_runtime_gate(policy, observation), "quarantined")

    def test_tampered_decision_digest_is_rejected(self):
        policy = RuntimePolicy()
        observation = RuntimeObservation("AI-SYS-001", "release-1", 10, 0, 0, 100, 0)
        decision = runtime_decision(policy, observation)
        object.__setattr__(decision, "decision_digest", "0" * 64)
        with self.assertRaisesRegex(RuntimeMonitorError, "decision_digest_mismatch"):
            verify_runtime_decision_context("AI-SYS-001", "release-1", decision)
