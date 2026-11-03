from decimal import Decimal
from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command, CommandError
from django.test import TestCase

from accounts.models import WorkerProfile
from promotions.models import Promotion
from tasks.models import Task
from wallet.models import WalletTransaction, WithdrawalRequest


class FinancialIntegrityPreflightTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="preflight_worker",
            password="test-password-123",
        )

    def test_preflight_reports_findings_without_modifying_records(self):
        task = Task.objects.create(
            title="Zero reward task",
            description="Preflight fixture",
            reward=Decimal("0.00"),
            max_workers=1,
        )
        WalletTransaction.objects.create(
            user=self.user,
            amount=Decimal("-2.00"),
            transaction_type="earning",
            description="Invalid earning fixture",
        )
        withdrawal = WithdrawalRequest.objects.create(
            user=self.user,
            amount=Decimal("-3.00"),
            bank_name="Test Bank",
            account_holder="Test Worker",
            bank_account="1234567890",
        )
        profile = WorkerProfile.objects.create(
            user=self.user,
            balance=Decimal("5.00"),
            reserved_balance=Decimal("6.00"),
            total_earned=Decimal("5.00"),
        )

        output = StringIO()
        call_command("financial_integrity_preflight", stdout=output)
        report = output.getvalue()

        self.assertIn("tasks.non_positive_reward: 1", report)
        self.assertIn("wallet.earning_non_positive: 1", report)
        self.assertIn("withdrawals.non_positive_amount: 1", report)
        self.assertIn("profiles.reserved_exceeds_balance: 1", report)
        self.assertIn("No records were modified.", report)

        task.refresh_from_db()
        withdrawal.refresh_from_db()
        profile.refresh_from_db()
        self.assertEqual(task.reward, Decimal("0.00"))
        self.assertEqual(withdrawal.amount, Decimal("-3.00"))
        self.assertEqual(profile.balance, Decimal("5.00"))
        self.assertEqual(profile.reserved_balance, Decimal("6.00"))

    def test_fail_on_findings_returns_error_without_mutation(self):
        Task.objects.create(
            title="Zero reward task",
            description="Preflight fixture",
            reward=Decimal("0.00"),
            max_workers=1,
        )

        with self.assertRaises(CommandError):
            call_command("financial_integrity_preflight", "--fail-on-findings")
