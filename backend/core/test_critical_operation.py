from datetime import timedelta
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from .critical_operation import require_critical_operation_authorized
from .models import OwnerApproval
from .owner_request_binding import canonical_request_digest
from .security_policy_engine import AuthorizationDenied


class CriticalOperationBoundaryTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(
            username="critical-owner",
            is_staff=True,
            is_superuser=True,
        )
        self.common = {
            "request_id": "req-001",
            "operation": "withdrawal.approve",
            "target": "withdrawal:123",
            "scope": "role_scope",
            "environment": "production",
            "policy_version": "test-v1",
            "material_parameters": {"withdrawal_id": 123, "decision": "approve"},
            "actor": "finance",
            "resource": "withdrawal",
            "action": "approve",
            "authorization_scope": "role_scope",
            "authorization_facts": {
                "permission.withdrawal_approve": True,
                "business_rules.valid_withdrawal": True,
            },
        }

    def _pair(self, *, digest, expires_at=None):
        expires_at = expires_at or (timezone.now() + timedelta(minutes=2))
        rows = []
        for device_id in ("device-a", "device-b"):
            rows.append(
                OwnerApproval.objects.create(
                    approval_id=uuid4(),
                    owner=self.owner,
                    device_id=device_id,
                    credential_id=f"credential-{device_id}",
                    request_digest=digest,
                    expires_at=expires_at,
                )
            )
        return tuple(row.approval_id for row in rows)

    def test_exact_binding_pair_is_consumed_and_authorizes(self):
        digest = canonical_request_digest(**{
            key: self.common[key]
            for key in (
                "request_id", "operation", "target", "scope",
                "environment", "policy_version", "material_parameters",
            )
        })
        ids = self._pair(digest=digest)
        with self._production_env():
            result = require_critical_operation_authorized(
                owner_id=self.owner.id,
                approval_ids=ids,
                **self.common,
            )
        self.assertEqual(result, digest)
        self.assertEqual(
            OwnerApproval.objects.filter(consumed_at__isnull=False).count(),
            2,
        )

    def test_parameter_mismatch_denies_and_does_not_consume_pair(self):
        digest = canonical_request_digest(**{
            key: self.common[key]
            for key in (
                "request_id", "operation", "target", "scope",
                "environment", "policy_version", "material_parameters",
            )
        })
        ids = self._pair(digest=digest)
        changed = {**self.common, "material_parameters": {"withdrawal_id": 124, "decision": "approve"}}
        with self._production_env():
            with self.assertRaises(AuthorizationDenied):
                require_critical_operation_authorized(
                    owner_id=self.owner.id,
                    approval_ids=ids,
                    **changed,
                )
        self.assertEqual(
            OwnerApproval.objects.filter(consumed_at__isnull=True).count(),
            2,
        )

    def test_policy_denial_rolls_back_consumption(self):
        digest = canonical_request_digest(**{
            key: self.common[key]
            for key in (
                "request_id", "operation", "target", "scope",
                "environment", "policy_version", "material_parameters",
            )
        })
        ids = self._pair(digest=digest)
        with self._production_env():
            with self.assertRaises(AuthorizationDenied):
                require_critical_operation_authorized(
                    owner_id=self.owner.id,
                    approval_ids=ids,
                    **{**self.common, "authorization_scope": "wrong-scope"},
                )
        self.assertEqual(
            OwnerApproval.objects.filter(consumed_at__isnull=True).count(),
            2,
        )

    def test_client_cannot_assert_dual_control_fact(self):
        digest = canonical_request_digest(**{
            key: self.common[key]
            for key in (
                "request_id", "operation", "target", "scope",
                "environment", "policy_version", "material_parameters",
            )
        })
        ids = self._pair(digest=digest)
        with self._production_env():
            with self.assertRaises(AuthorizationDenied):
                require_critical_operation_authorized(
                    owner_id=self.owner.id,
                    approval_ids=ids,
                    **{
                        **self.common,
                        "authorization_facts": {
                            **self.common["authorization_facts"],
                            "owner_dual_control_verified": True,
                        },
                    },
                )
        self.assertEqual(
            OwnerApproval.objects.filter(consumed_at__isnull=False).count(),
            0,
        )

    def test_replay_denies_after_successful_consumption(self):
        digest = canonical_request_digest(**{
            key: self.common[key]
            for key in (
                "request_id", "operation", "target", "scope",
                "environment", "policy_version", "material_parameters",
            )
        })
        ids = self._pair(digest=digest)
        with self._production_env():
            require_critical_operation_authorized(
                owner_id=self.owner.id,
                approval_ids=ids,
                **self.common,
            )
            with self.assertRaises(AuthorizationDenied):
                require_critical_operation_authorized(
                    owner_id=self.owner.id,
                    approval_ids=ids,
                    **self.common,
                )

    class _production_env:
        def __enter__(self):
            import os
            self.old = {
                "PRODUCTION_MODE": os.environ.get("PRODUCTION_MODE"),
                "OWNER_CONTROL_STATE": os.environ.get("OWNER_CONTROL_STATE"),
            }
            os.environ["PRODUCTION_MODE"] = "true"
            os.environ["OWNER_CONTROL_STATE"] = "PRODUCTION_DUAL_CONTROL"

        def __exit__(self, exc_type, exc, tb):
            import os
            for key, value in self.old.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
