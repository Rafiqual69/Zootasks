from django.test import SimpleTestCase

from .security_policy_engine import authorize


class AutomationPolicyTests(SimpleTestCase):
    def test_system_task_creation_requires_all_bounded_facts(self):
        facts = {
            "trusted_execution_context": True,
            "automation.task_template_allowlisted": True,
            "automation.reward_bounded": True,
        }
        self.assertTrue(
            authorize(
                actor="system",
                resource="task",
                action="create",
                scope="global",
                facts=facts,
            )
        )
        for missing in facts:
            incomplete = dict(facts)
            incomplete.pop(missing)
            self.assertFalse(
                authorize(
                    actor="system",
                    resource="task",
                    action="create",
                    scope="global",
                    facts=incomplete,
                )
            )

    def test_system_task_expiry_requires_lifecycle_bounds(self):
        facts = {
            "trusted_execution_context": True,
            "automation.lifecycle_maintenance": True,
            "automation.status_transition_bounded": True,
        }
        self.assertTrue(
            authorize(
                actor="system",
                resource="task",
                action="update",
                scope="global",
                facts=facts,
            )
        )
        tampered = dict(facts)
        tampered["automation.status_transition_bounded"] = False
        self.assertFalse(
            authorize(
                actor="system",
                resource="task",
                action="update",
                scope="global",
                facts=tampered,
            )
        )

    def test_unknown_system_financial_write_denies(self):
        self.assertFalse(
            authorize(
                actor="system",
                resource="wallet",
                action="update",
                scope="global",
                facts={"trusted_execution_context": True},
            )
        )
