from decimal import Decimal

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase

from .models import WalletTransaction, WithdrawalRequest


class WithdrawalDatabaseInvariantTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="withdrawal_invariant_worker",
            password="test-password-123",
        )

    def test_negative_withdrawal_amount_is_rejected_by_database_constraint(self):
        with self.assertRaises(IntegrityError):
            WithdrawalRequest.objects.create(
                user=self.user,
                amount=Decimal("-0.01"),
                bank_account="1234567890",
                bank_name="Test Bank",
                account_holder="Test Worker",
            )

    def test_zero_withdrawal_amount_is_allowed_by_row_constraint(self):
        withdrawal = WithdrawalRequest.objects.create(
            user=self.user,
            amount=Decimal("0.00"),
            bank_account="1234567890",
            bank_name="Test Bank",
            account_holder="Test Worker",
        )
        self.assertEqual(withdrawal.amount, Decimal("0.00"))


class WalletTransactionAmountInvariantTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="wallet_tx_invariant_worker",
            password="test-password-123",
        )

    def test_negative_earning_amount_is_rejected_by_database_constraint(self):
        with self.assertRaises(IntegrityError):
            WalletTransaction.objects.create(
                user=self.user,
                amount=Decimal("-0.01"),
                transaction_type="earning",
                description="Synthetic invalid earning",
            )

    def test_negative_withdrawal_transaction_amount_is_rejected(self):
        with self.assertRaises(IntegrityError):
            WalletTransaction.objects.create(
                user=self.user,
                amount=Decimal("-0.01"),
                transaction_type="withdrawal",
                description="Synthetic invalid withdrawal",
            )

    def test_negative_adjustment_remains_supported(self):
        transaction = WalletTransaction.objects.create(
            user=self.user,
            amount=Decimal("-1.00"),
            transaction_type="adjustment",
            description="Synthetic adjustment test",
        )
        self.assertEqual(transaction.amount, Decimal("-1.00"))
