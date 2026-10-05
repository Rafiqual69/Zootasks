from .security_policy import load_and_validate_policy
from .security_policy_engine import AuthorizationDenied, authorize, require_authorized
import unittest


class SecurityPolicyDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = load_and_validate_policy()

    def test_worker_task_read_requires_server_side_fact(self):
        self.assertFalse(
            authorize(
                actor="worker",
                resource="task",
                action="read",
                scope="role_scope",
                facts={},
            )
        )
        self.assertTrue(
            authorize(
                actor="worker",
                resource="task",
                action="read",
                scope="role_scope",
                facts={"account_entity.active_worker": True},
            )
        )

    def test_unknown_operation_denies(self):
        self.assertFalse(
            authorize(
                actor="worker",
                resource="wallet",
                action="export",
                scope="global",
                facts={"account_entity.active_worker": True},
            )
        )

    def test_ai_financial_operations_deny(self):
        for action, resource in (
            ("update", "wallet"),
            ("create", "wallet_transaction"),
            ("approve", "withdrawal"),
            ("pay", "withdrawal"),
        ):
            self.assertFalse(
                authorize(
                    actor="ai",
                    resource=resource,
                    action=action,
                    scope="none",
                    facts={"ai_financial_boundary": True},
                )
            )

    def test_worker_claim_requires_role_fact(self):
        self.assertFalse(
            authorize(
                actor="worker",
                resource="task",
                action="claim",
                scope="role_scope",
                facts={},
            )
        )
        self.assertTrue(
            authorize(
                actor="worker",
                resource="task",
                action="claim",
                scope="role_scope",
                facts={
                    "account_entity.active_worker": True,
                    "task.active": True,
                    "task.capacity_available": True,
                    "request.method.POST": True,
                },
            )
        )

    def test_owner_access_is_not_granted_by_partial_facts(self):
        self.assertFalse(
            authorize(
                actor="owner",
                resource="account_entity",
                action="manage_access",
                scope="global",
                facts={"owner_authenticated": True},
            )
        )

    def test_require_authorized_raises_on_deny(self):
        with self.assertRaises(AuthorizationDenied):
            require_authorized(
                actor="worker",
                resource="wallet",
                action="update",
                scope="own",
                facts={"account_entity.active_worker": True},
            )


if __name__ == "__main__":
    unittest.main()
