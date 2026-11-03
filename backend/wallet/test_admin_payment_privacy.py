from django.contrib import admin
from django.contrib.auth.models import Permission, User
from django.test import RequestFactory, TestCase

from wallet.admin import WithdrawalRequestAdmin
from wallet.models import WithdrawalRequest


class WithdrawalPaymentDetailPrivacyTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.model_admin = WithdrawalRequestAdmin(
            WithdrawalRequest,
            admin.site,
        )

    def request_for(self, user):
        request = self.factory.get("/admin/wallet/withdrawalrequest/")
        request.user = user
        return request

    def staff_with_permission(self, username, codename):
        user = User.objects.create_user(
            username=username,
            password="test-password-123",
            is_staff=True,
        )
        user.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="wallet",
                codename=codename,
            )
        )
        return user

    def test_approver_sees_masked_payment_details_only(self):
        approver = self.staff_with_permission(
            "withdrawal_approver_privacy",
            "approve_withdrawal",
        )

        fields = set(self.model_admin.get_fields(self.request_for(approver)))

        self.assertIn("masked_account_holder", fields)
        self.assertIn("masked_bank_account", fields)
        self.assertNotIn("account_holder", fields)
        self.assertNotIn("bank_account", fields)

    def test_rejector_sees_masked_payment_details_only(self):
        rejector = self.staff_with_permission(
            "withdrawal_rejector_privacy",
            "reject_withdrawal",
        )

        fields = set(self.model_admin.get_fields(self.request_for(rejector)))

        self.assertIn("masked_account_holder", fields)
        self.assertIn("masked_bank_account", fields)
        self.assertNotIn("account_holder", fields)
        self.assertNotIn("bank_account", fields)

    def test_payer_can_view_read_only_payment_details(self):
        payer = self.staff_with_permission(
            "withdrawal_payer_privacy",
            "mark_withdrawal_paid",
        )

        fields = set(self.model_admin.get_fields(self.request_for(payer)))

        self.assertIn("account_holder", fields)
        self.assertIn("bank_account", fields)
        self.assertNotIn("masked_account_holder", fields)
        self.assertNotIn("masked_bank_account", fields)
        self.assertIn("account_holder", self.model_admin.readonly_fields)
        self.assertIn("bank_account", self.model_admin.readonly_fields)

    def test_unprivileged_staff_cannot_view_withdrawal_details(self):
        staff = User.objects.create_user(
            username="withdrawal_unprivileged_privacy",
            password="test-password-123",
            is_staff=True,
        )

        self.assertFalse(
            self.model_admin.has_view_permission(self.request_for(staff))
        )

    def test_superuser_can_view_read_only_payment_details(self):
        owner = User.objects.create_superuser(
            username="withdrawal_owner_privacy",
            password="test-password-123",
            email="owner-privacy@example.com",
        )

        fields = set(self.model_admin.get_fields(self.request_for(owner)))

        self.assertIn("account_holder", fields)
        self.assertIn("bank_account", fields)
        self.assertIn("account_holder", self.model_admin.readonly_fields)
        self.assertIn("bank_account", self.model_admin.readonly_fields)
