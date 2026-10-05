from datetime import timedelta

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.utils import timezone

from accounts.models import AccountEntity
from core.admin_dashboard import _owner_dashboard_facts
from core.security_policy_engine import authorize


class LiveWalletDashboardSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.owner = User.objects.create_user(
            username="owner-test",
            password="safe-test-password",
            is_staff=True,
            is_superuser=True,
        )
        AccountEntity.objects.create(
            user=self.owner,
            entity_type=AccountEntity.EntityType.OWNER,
            is_active=True,
        )

    def _request(self, user, reauth_at=None):
        request = self.factory.get("/admin/live-wallet/")
        request.user = user
        request.session = {}
        if reauth_at is not None:
            request.session["owner_reauthenticated_at"] = reauth_at.isoformat()
        return request

    def test_owner_dashboard_requires_all_privileged_facts(self):
        request = self._request(self.owner, timezone.now())
        facts = _owner_dashboard_facts(request)

        self.assertTrue(
            authorize(
                actor="owner",
                resource="admin_wallet_dashboard",
                action="read",
                scope="global",
                facts=facts,
            )
        )

    def test_stale_owner_reauthentication_denies_dashboard(self):
        stale = timezone.now() - timedelta(minutes=16)
        request = self._request(self.owner, stale)
        facts = _owner_dashboard_facts(request)

        self.assertFalse(
            authorize(
                actor="owner",
                resource="admin_wallet_dashboard",
                action="read",
                scope="global",
                facts=facts,
            )
        )

    def test_staff_superuser_without_canonical_owner_boundary_denies(self):
        staff = User.objects.create_user(
            username="staff-test",
            password="safe-test-password",
            is_staff=True,
            is_superuser=True,
        )
        request = self._request(staff, timezone.now())
        facts = _owner_dashboard_facts(request)

        self.assertFalse(
            authorize(
                actor="owner",
                resource="admin_wallet_dashboard",
                action="read",
                scope="global",
                facts=facts,
            )
        )
