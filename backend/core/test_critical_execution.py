from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, SimpleTestCase

from .critical_execution import SESSION_KEY, require_execution_authorized
from .security_policy_engine import AuthorizationDenied


class CriticalExecutionBridgeTests(SimpleTestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="critical-execution-owner",
            is_staff=True,
            is_superuser=True,
        )
        self.request = RequestFactory().post("/admin/")
        self.request.user = self.user

        class Session(dict):
            modified = False

        self.request.session = Session()

    def _kwargs(self):
        return {
            "request": self.request,
            "actor": "finance",
            "operation": "withdrawal.approve",
            "target": "withdrawal:1",
            "resource": "withdrawal",
            "action": "approve",
            "material_parameters": {
                "withdrawal_id": 1,
                "user_id": self.user.id,
                "amount": "10.00",
                "status": "pending",
            },
            "authorization_facts": {
                "permission.withdrawal_approve": True,
                "business_rules.valid_withdrawal": True,
            },
        }

    @patch("core.critical_execution.settings.PRODUCTION_MODE", False)
    def test_development_uses_existing_policy_path(self):
        self.assertIsNone(require_execution_authorized(**self._kwargs()))

    @patch("core.critical_execution.settings.PRODUCTION_MODE", True)
    @patch("core.critical_execution.settings.OWNER_CONTROL_STATE", "PRODUCTION_DUAL_CONTROL")
    def test_production_denies_without_server_created_context(self):
        with self.assertRaises(AuthorizationDenied):
            require_execution_authorized(**self._kwargs())

    @patch("core.critical_execution.settings.PRODUCTION_MODE", True)
    @patch("core.critical_execution.settings.OWNER_CONTROL_STATE", "SECURITY_FREEZE")
    def test_security_freeze_cannot_be_bypassed(self):
        with self.assertRaises(AuthorizationDenied):
            require_execution_authorized(**self._kwargs())
