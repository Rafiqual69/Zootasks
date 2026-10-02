from django.test import SimpleTestCase
from core.ai_provider_circuit_breaker import CircuitBreakerError,CircuitPolicy,CircuitState,allow_call,record_result

class AIProviderCircuitBreakerTests(SimpleTestCase):
    def test_success_keeps_circuit_closed(self):
        self.assertEqual(record_result(CircuitPolicy(),CircuitState(),True).state,"closed")
    def test_failure_threshold_opens(self):
        p=CircuitPolicy(max_failures=2)
        s=record_result(p,CircuitState(),False)
        self.assertEqual(record_result(p,s,False).state,"open")
    def test_call_budget_opens(self):
        p=CircuitPolicy(max_calls=2)
        s=record_result(p,CircuitState(),True)
        self.assertEqual(record_result(p,s,True).state,"open")
    def test_external_effect_budget_is_zero(self):
        with self.assertRaisesRegex(CircuitBreakerError,"external_effect_budget_must_be_zero"):
            allow_call(CircuitPolicy(max_external_effects=1),CircuitState())
    def test_open_circuit_stays_open(self):
        s=allow_call(CircuitPolicy(max_failures=1),CircuitState(failures=1))
        self.assertEqual(s.state,"open")
