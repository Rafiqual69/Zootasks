from unittest.mock import patch

from django.test import SimpleTestCase

from .security_policy_engine import authorize


class ProductionDualControlOverlayTests(SimpleTestCase):
    def test_critical_operation_denied_in_production_without_explicit_dual_state(self):
        with patch.dict(
            "os.environ",
            {"PRODUCTION_MODE": "true"},
            clear=False,
        ):
            self.assertFalse(
                authorize(
                    actor="finance",
                    resource="withdrawal",
                    action="approve",
                    scope="role_scope",
                    facts={
                        "permission.withdrawal_approve": True,
                        "business_rules.valid_withdrawal": True,
                    },
                )
            )

    def test_critical_operation_denied_in_readiness_state(self):
        with patch.dict(
            "os.environ",
            {
                "PRODUCTION_MODE": "true",
                "OWNER_CONTROL_STATE": "PRODUCTION_READINESS_PENDING",
            },
            clear=False,
        ):
            self.assertFalse(
                authorize(
                    actor="finance_payer",
                    resource="withdrawal",
                    action="pay",
                    scope="role_scope",
                    facts={
                        "permission.withdrawal_pay": True,
                        "business_rules.approved_withdrawal": True,
                        "idempotency.required": True,
                        "owner_dual_control_verified": True,
                    },
                )
            )

    def test_critical_operation_requires_verified_dual_control(self):
        base_facts = {
            "permission.withdrawal_approve": True,
            "business_rules.valid_withdrawal": True,
        }
        with patch.dict(
            "os.environ",
            {
                "PRODUCTION_MODE": "true",
                "OWNER_CONTROL_STATE": "PRODUCTION_DUAL_CONTROL",
            },
            clear=False,
        ):
            self.assertFalse(
                authorize(
                    actor="finance",
                    resource="withdrawal",
                    action="approve",
                    scope="role_scope",
                    facts=base_facts,
                )
            )
            self.assertTrue(
                authorize(
                    actor="finance",
                    resource="withdrawal",
                    action="approve",
                    scope="role_scope",
                    facts={
                        **base_facts,
                        "owner_dual_control_verified": True,
                    },
                )
            )

    def test_security_freeze_denies_critical_operation(self):
        with patch.dict(
            "os.environ",
            {
                "PRODUCTION_MODE": "true",
                "OWNER_CONTROL_STATE": "SECURITY_FREEZE",
            },
            clear=False,
        ):
            self.assertFalse(
                authorize(
                    actor="finance",
                    resource="withdrawal",
                    action="approve",
                    scope="role_scope",
                    facts={
                        "permission.withdrawal_approve": True,
                        "business_rules.valid_withdrawal": True,
                        "owner_dual_control_verified": True,
                    },
                )
            )

    def test_noncritical_operation_is_not_changed_by_overlay(self):
        with patch.dict(
            "os.environ",
            {
                "PRODUCTION_MODE": "true",
                "OWNER_CONTROL_STATE": "PRODUCTION_READINESS_PENDING",
            },
            clear=False,
        ):
            self.assertTrue(
                authorize(
                    actor="worker",
                    resource="task",
                    action="read",
                    scope="role_scope",
                    facts={"account_entity.active_worker": True},
                )
            )
