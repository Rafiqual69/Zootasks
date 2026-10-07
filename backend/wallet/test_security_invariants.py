from decimal import Decimal

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase

from .models import WithdrawalRequest


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
