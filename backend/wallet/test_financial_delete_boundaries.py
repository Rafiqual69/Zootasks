from decimal import Decimal

from django.contrib.auth.models import User
from django.db.models import ProtectedError
from django.test import TestCase

from accounts.models import WorkerProfile
from promotions.models import Promotion, PromotionClaim
from tasks.models import Task, TaskClaim
from wallet.models import WalletTransaction, WithdrawalRequest


class FinancialDeleteBoundaryTests(TestCase):
    def test_task_delete_cannot_remove_claim_history(self):
        worker = User.objects.create_user(username="delete_task_worker")
        task = Task.objects.create(
            title="Protected task",
            description="Synthetic task",
            reward=Decimal("10.00"),
        )
        claim = TaskClaim.objects.create(task=task, worker=worker)

        with self.assertRaises(ProtectedError):
            task.delete()

        self.assertTrue(Task.objects.filter(pk=task.pk).exists())
        self.assertTrue(TaskClaim.objects.filter(pk=claim.pk).exists())

    def test_promotion_delete_cannot_remove_claim_history(self):
        worker = User.objects.create_user(username="delete_promotion_worker")
        promotion = Promotion.objects.create(
            title="Protected promotion",
            description="Synthetic promotion",
            advertiser_name="Synthetic advertiser",
            reward=Decimal("10.00"),
            budget=Decimal("20.00"),
        )
        claim = PromotionClaim.objects.create(
            promotion=promotion,
            worker=worker,
        )

        with self.assertRaises(ProtectedError):
            promotion.delete()

        self.assertTrue(Promotion.objects.filter(pk=promotion.pk).exists())
        self.assertTrue(PromotionClaim.objects.filter(pk=claim.pk).exists())

    def test_user_delete_cannot_remove_worker_balance_history(self):
        worker = User.objects.create_user(username="delete_balance_worker")
        profile = WorkerProfile.objects.create(
            user=worker,
            balance=Decimal("25.00"),
            reserved_balance=Decimal("5.00"),
            total_earned=Decimal("30.00"),
        )

        with self.assertRaises(ProtectedError):
            worker.delete()

        profile.refresh_from_db()
        self.assertEqual(profile.balance, Decimal("25.00"))
        self.assertTrue(User.objects.filter(pk=worker.pk).exists())

    def test_user_delete_cannot_remove_wallet_ledger(self):
        worker = User.objects.create_user(username="delete_ledger_worker")
        transaction = WalletTransaction.objects.create(
            user=worker,
            amount=Decimal("15.00"),
            transaction_type="earning",
            description="Synthetic ledger entry",
        )

        with self.assertRaises(ProtectedError):
            worker.delete()

        self.assertTrue(User.objects.filter(pk=worker.pk).exists())
        self.assertTrue(
            WalletTransaction.objects.filter(pk=transaction.pk).exists()
        )

    def test_user_delete_cannot_remove_withdrawal_history(self):
        worker = User.objects.create_user(username="delete_withdrawal_worker")
        withdrawal = WithdrawalRequest.objects.create(
            user=worker,
            amount=Decimal("50.00"),
            bank_account="synthetic-account",
            bank_name="Synthetic Bank",
            account_holder="Synthetic Worker",
        )

        with self.assertRaises(ProtectedError):
            worker.delete()

        self.assertTrue(User.objects.filter(pk=worker.pk).exists())
        self.assertTrue(
            WithdrawalRequest.objects.filter(pk=withdrawal.pk).exists()
        )

    def test_user_delete_cannot_remove_task_claim_history(self):
        worker = User.objects.create_user(username="delete_task_claim_worker")
        task = Task.objects.create(
            title="Claim retention task",
            description="Synthetic task",
            reward=Decimal("5.00"),
        )
        claim = TaskClaim.objects.create(task=task, worker=worker)

        with self.assertRaises(ProtectedError):
            worker.delete()

        self.assertTrue(User.objects.filter(pk=worker.pk).exists())
        self.assertTrue(TaskClaim.objects.filter(pk=claim.pk).exists())

    def test_user_delete_cannot_remove_promotion_claim_history(self):
        worker = User.objects.create_user(username="delete_promotion_claim_worker")
        promotion = Promotion.objects.create(
            title="Claim retention promotion",
            description="Synthetic promotion",
            advertiser_name="Synthetic advertiser",
            reward=Decimal("5.00"),
            budget=Decimal("10.00"),
        )
        claim = PromotionClaim.objects.create(
            promotion=promotion,
            worker=worker,
        )

        with self.assertRaises(ProtectedError):
            worker.delete()

        self.assertTrue(User.objects.filter(pk=worker.pk).exists())
        self.assertTrue(
            PromotionClaim.objects.filter(pk=claim.pk).exists()
        )
