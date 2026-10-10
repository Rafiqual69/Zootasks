from django.test import SimpleTestCase

from .ai_circuit_breaker import AICostBudget, validate_ai_budget, validate_step_cost
from .ai_control_plane import AIGuardError

class AICircuitBreakerTests(SimpleTestCase):
    def test_normal_budget_is_allowed(self):
        validate_ai_budget(cost_units=10, tool_calls=2, retries=1)

    def test_cost_limit_fails_closed(self):
        with self.assertRaises(AIGuardError):
            validate_ai_budget(cost_units=101, tool_calls=1, retries=0)

    def test_tool_call_limit_fails_closed(self):
        with self.assertRaises(AIGuardError):
            validate_ai_budget(cost_units=1, tool_calls=13, retries=0)

    def test_retry_limit_fails_closed(self):
        with self.assertRaises(AIGuardError):
            validate_ai_budget(cost_units=1, tool_calls=1, retries=13)

    def test_custom_budget_is_enforced(self):
        with self.assertRaises(AIGuardError):
            validate_ai_budget(cost_units=11, tool_calls=1, retries=0, budget=AICostBudget(max_cost_units=10))

    def test_step_cost_is_bounded(self):
        validate_step_cost(25)
        with self.assertRaises(AIGuardError):
            validate_step_cost(26)
