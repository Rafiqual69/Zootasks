from uuid import uuid4
from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.utils import timezone

from .execution_authorization import _APPROVAL_SESSION_KEY, require_execution_authorized
from .models import OwnerApproval
from .owner_request_binding import canonical_request_digest
from .security_policy import load_and_validate_policy
from .security_policy_engine import AuthorizationDenied


class ExecutionAuthorizationBridgeTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(
            username="execution-owner",
            is_staff=True,
            is_superuser=True,
        )
        self.factory = RequestFactory()

    def _request(self):
        request = self.factory.post("/admin/test/")
        request.user = self.owner
        SessionMiddleware(lambda req: None).process_request(request)
        request.session.save()
        return request

    def _common(self):
        return {
            "operation": "withdrawal.approve",
            "target": "withdrawal:123",
            "scope": "role_scope",
            "material_parameters": {
                "withdrawal_id": 123,
                "amount": "25.00",
                "status": "pending",
            },
            "actor": "finance",
            "resource": "withdrawal",
            "action": "approve",
            "authorization_scope": "role_scope",
            "authorization_facts": {
                "permission.withdrawal_approve": True,
                "business_rules.valid_withdrawal": True,
            },
        }

    def _digest(self, request_id):
        common = self._common()
        return canonical_request_digest(
            request_id=request_id,
            operation=common["operation"],
            target=common["target"],
            scope=common["scope"],
            environment="production",
            policy_version=load_and_validate_policy()["policy_version"],
            material_parameters=common["material_parameters"],
        )

    def _pair(self, digest):
        rows = [
            OwnerApproval.objects.create(
                approval_id=uuid4(),
                owner=self.owner,
                device_id=device,
                credential_id=f"credential-{device}",
                request_digest=digest,
                expires_at=timezone.now() + timedelta(minutes=2),
            )
            for device in ("device-a", "device-b")
        ]
        return [str(row.approval_id) for row in rows]

    def test_production_denies_without_server_approval_context(self):
        request = self._request()
        with patch.dict("os.environ", {"PRODUCTION_MODE": "true", "OWNER_CONTROL_STATE": "PRODUCTION_DUAL_CONTROL"}, clear=False):
            with self.assertRaises(PermissionError):
                require_execution_authorized(
                    request=request,
                    **self._common(),
                )

    def test_client_cannot_supply_approval_ids_outside_server_session(self):
        request = self._request()
        request.POST = request.POST.copy()
        request.POST["approval_ids"] = str(uuid4())
        with self.settings(PRODUCTION_MODE=True):
            with self.assertRaises(PermissionError):
                require_execution_authorized(
                    request=request,
                    **self._common(),
                )

    def test_valid_server_context_consumes_pair_and_clears_context(self):
        request = self._request()
        request_id = "execution-request-001"
        digest = self._digest(request_id)
        approval_ids = self._pair(digest)
        request.session[_APPROVAL_SESSION_KEY] = {
            "request_id": request_id,
            "approval_ids": approval_ids,
        }
        request.session.save()

        with patch.dict("os.environ", {"PRODUCTION_MODE": "true", "OWNER_CONTROL_STATE": "PRODUCTION_DUAL_CONTROL"}, clear=False):
            result = require_execution_authorized(
                request=request,
                **self._common(),
            )

        self.assertIsNotNone(result)
        self.assertEqual(
            OwnerApproval.objects.filter(consumed_at__isnull=False).count(),
            2,
        )
        self.assertNotIn(_APPROVAL_SESSION_KEY, request.session)

    def test_malformed_server_context_denies(self):
        request = self._request()
        request.session[_APPROVAL_SESSION_KEY] = {
            "request_id": "req",
            "approval_ids": ["not-a-uuid", "also-invalid"],
        }
        request.session.save()

        with self.settings(PRODUCTION_MODE=True, OWNER_CONTROL_STATE="PRODUCTION_DUAL_CONTROL"):
            with self.assertRaises(PermissionError):
                require_execution_authorized(
                    request=request,
                    **self._common(),
                )

    def test_development_keeps_existing_policy_path(self):
        request = self._request()
        with patch.dict("os.environ", {"PRODUCTION_MODE": "false"}, clear=False):
            result = require_execution_authorized(
                request=request,
                **self._common(),
            )
        self.assertIsNone(result)
