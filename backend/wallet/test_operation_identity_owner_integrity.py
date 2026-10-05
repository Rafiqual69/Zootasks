from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import Permission, User
from django.test import TestCase, RequestFactory

from accounts.models import WorkerProfile
from promotions.models import Promotion, PromotionClaim
from tasks.models import Task, TaskClaim
from wallet.admin import WithdrawalRequestAdmin, mark_withdrawals_paid
from wallet.models import WalletTransaction, WithdrawalRequest


class OperationIdentityOwnerIntegrityTests(TestCase):
    """Bound ledger identity must also match the business-operation owner."""

    def setUp(self):
        self.factory = RequestFactory()
        self.finance = User.objects.create_user(username="finance_identity", password="test")
        self.finance.is_staff = True
        self.finance.save(update_fields=["is_staff"])
        self.payer = User.objects.create_user(username="payer_identity", password="test")
        self.payer.is_staff = True
        self.payer.save(update_fields=["is_staff"])
        self.worker = User.objects.create_user(username="operation_owner", password="test")
        self.other = User.objects.create_user(username="wrong_ledger_owner", password="test")
        WorkerProfile.objects.create(user=self.worker, balance=Decimal("100.00"), reserved_balance=Decimal("50.00"))

    def _grant(self, user, app_label, codename):
        user.user_permissions.add(Permission.objects.get(content_type__app_label=app_label, codename=codename))

    def test_withdrawal_bound_ledger_with_wrong_owner_does_not_mark_paid(self):
        self._grant(self.payer, "wallet", "mark_withdrawal_paid")
        withdrawal = WithdrawalRequest.objects.create(
            user=self.worker,
            amount=Decimal("50.00"),
            bank_name="Safe Bank",
            account_holder="Worker",
            bank_account="1234567890",
            status="approved",
        )
        WalletTransaction.objects.create(
            user=self.other,
            amount=withdrawal.amount,
            transaction_type="withdrawal",
            description=f"Withdrawal #{withdrawal.id}",
            withdrawal=withdrawal,
        )
        request = self.factory.post("/admin/wallet/withdrawalrequest/")
        request.user = self.payer
        modeladmin = WithdrawalRequestAdmin(WithdrawalRequest, __import__("django.contrib").contrib.admin.site)

        with patch("wallet.admin.require_authorized"):
            mark_withdrawals_paid(modeladmin, request, WithdrawalRequest.objects.filter(pk=withdrawal.pk))

        withdrawal.refresh_from_db()
        profile = WorkerProfile.objects.get(user=self.worker)
        self.assertEqual(withdrawal.status, "approved")
        self.assertEqual(profile.balance, Decimal("100.00"))
        self.assertEqual(profile.reserved_balance, Decimal("50.00"))

    def test_task_bound_ledger_with_wrong_owner_does_not_approve(self):
        from tasks.admin import TaskClaimAdmin, approve_submissions
        task = Task.objects.create(title="Identity task", description="Test", reward=Decimal("25.00"))
        claim = TaskClaim.objects.create(task=task, worker=self.worker, status="submitted")
        WalletTransaction.objects.create(
            user=self.other,
            amount=Decimal("25.00"),
            transaction_type="earning",
            description="Wrong owner ledger",
            task_claim=claim,
        )
        self._grant(self.finance, "tasks", "approve_task_submission")
        request = self.factory.post("/admin/tasks/taskclaim/")
        request.user = self.finance
        modeladmin = TaskClaimAdmin(TaskClaim, __import__("django.contrib").contrib.admin.site)

        with patch("tasks.admin.require_authorized"):
            approve_submissions(modeladmin, request, TaskClaim.objects.filter(pk=claim.pk))

        claim.refresh_from_db()
        profile = WorkerProfile.objects.get(user=self.worker)
        self.assertEqual(claim.status, "submitted")
        self.assertEqual(profile.balance, Decimal("100.00"))

    def test_promotion_bound_ledger_with_wrong_owner_does_not_approve(self):
        from promotions.admin import PromotionClaimAdmin
        promotion = Promotion.objects.create(
            title="Identity promotion",
            description="Test",
            advertiser_name="Advertiser",
            reward=Decimal("25.00"),
        )
        claim = PromotionClaim.objects.create(promotion=promotion, worker=self.worker, status="submitted")
        WalletTransaction.objects.create(
            user=self.other,
            amount=Decimal("25.00"),
            transaction_type="earning",
            description="Wrong owner ledger",
            promotion_claim=claim,
        )
        self._grant(self.finance, "promotions", "approve_promotion_claim")
        request = self.factory.post("/admin/promotions/promotionclaim/")
        request.user = self.finance
        modeladmin = PromotionClaimAdmin(PromotionClaim, __import__("django.contrib").contrib.admin.site)

        with patch("promotions.admin.require_authorized"):
            modeladmin.approve_claims(request, PromotionClaim.objects.filter(pk=claim.pk))

        claim.refresh_from_db()
        profile = WorkerProfile.objects.get(user=self.worker)
        self.assertEqual(claim.status, "submitted")
        self.assertEqual(profile.balance, Decimal("100.00"))
