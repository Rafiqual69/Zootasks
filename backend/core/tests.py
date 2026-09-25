from django.contrib import admin
from django.contrib.auth.models import Group, Permission, User
from django.core.management import call_command
from django.test import RequestFactory, TestCase
from django.urls import reverse

from wallet.models import WalletTransaction, WithdrawalRequest


class LiveWalletDashboardPermissionTests(TestCase):
    def setUp(self):
        self.url = reverse("live_wallet_dashboard")
        self.staff = User.objects.create_user(
            username="finance_viewer",
            password="test-password-123",
            is_staff=True,
        )
        self.permission = Permission.objects.get(
            content_type__app_label="wallet",
            codename="view_live_wallet_dashboard",
        )

    def test_staff_without_dashboard_permission_is_forbidden(self):
        self.client.force_login(self.staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_staff_with_dashboard_permission_can_view_dashboard(self):
        self.staff.user_permissions.add(self.permission)
        self.client.force_login(self.staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Live Wallet Dashboard")
        self.assertContains(response, "Finance Control Center")
        self.assertContains(response, "Withdrawal control")
        self.assertContains(response, "Controlled finance lifecycle")
        self.assertContains(response, "Request")
        self.assertContains(response, "Reconcile")

    def test_superuser_can_view_dashboard_without_explicit_permission(self):
        self.staff.is_superuser = True
        self.staff.save(update_fields=["is_superuser"])
        self.client.force_login(self.staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)


class FinanceRBACSetupTests(TestCase):
    def setUp(self):
        self.pay = Permission.objects.get(
            content_type__app_label="wallet",
            codename="mark_withdrawal_paid",
        )
        self.dashboard = Permission.objects.get(
            content_type__app_label="wallet",
            codename="view_live_wallet_dashboard",
        )
        self.approve = Permission.objects.get(
            content_type__app_label="wallet",
            codename="approve_withdrawal",
        )
        self.reject = Permission.objects.get(
            content_type__app_label="wallet",
            codename="reject_withdrawal",
        )

    def test_setup_rbac_separates_finance_approval_and_payment(self):
        call_command("setup_rbac")

        finance = Group.objects.get(name="Finance")
        payer = Group.objects.get(name="Finance Payer")
        super_admin = Group.objects.get(name="Super Admin")

        self.assertTrue(finance.permissions.filter(pk=self.approve.pk).exists())
        self.assertTrue(finance.permissions.filter(pk=self.reject.pk).exists())
        self.assertTrue(finance.permissions.filter(pk=self.dashboard.pk).exists())
        self.assertFalse(finance.permissions.filter(pk=self.pay.pk).exists())

        self.assertTrue(payer.permissions.filter(pk=self.pay.pk).exists())
        self.assertTrue(payer.permissions.filter(pk=self.dashboard.pk).exists())
        self.assertFalse(payer.permissions.filter(pk=self.approve.pk).exists())
        self.assertFalse(payer.permissions.filter(pk=self.reject.pk).exists())

        self.assertTrue(
            super_admin.permissions.filter(pk=self.dashboard.pk).exists()
        )


class PrivilegedFinanceSecurityAuditTests(TestCase):
    def test_security_audit_passes_after_rbac_setup(self):
        call_command("setup_rbac")
        call_command("audit_security")

    def test_wallet_financial_records_are_not_directly_editable_in_admin(self):
        request = RequestFactory().get("/admin/")
        request.user = User.objects.create_superuser(
            username="audit_admin",
            password="test-password-123",
        )

        wallet_admin = admin.site._registry[WalletTransaction]
        withdrawal_admin = admin.site._registry[WithdrawalRequest]

        for model_admin in (wallet_admin, withdrawal_admin):
            self.assertFalse(model_admin.has_add_permission(request))
            self.assertFalse(model_admin.has_change_permission(request))
            self.assertFalse(model_admin.has_delete_permission(request))
