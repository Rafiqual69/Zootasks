from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import WorkerProfile
from wallet.models import WalletTransaction, WithdrawalRequest
from wallet.admin import approve_withdrawals, reject_withdrawals, mark_withdrawals_paid


class WithdrawalFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="worker_test",
            password="test-password-123",
        )
        self.profile = WorkerProfile.objects.create(
            user=self.user,
            balance=Decimal("200.00"),
            reserved_balance=Decimal("0.00"),
            total_earned=Decimal("200.00"),
        )
        self.client.login(
            username="worker_test",
            password="test-password-123",
        )

    def withdrawal_data(self, amount="50.00"):
        return {
            "amount": amount,
            "bank_name": "Test Bank",
            "account_holder": "Test Worker",
            "bank_account": "1234567890",
        }

    def test_valid_withdrawal_reserves_balance(self):
        response = self.client.post(
            reverse("request_withdrawal"),
            self.withdrawal_data("50.00"),
        )

        self.assertRedirects(response, reverse("withdrawal_success"))

        self.profile.refresh_from_db()
        withdrawal = WithdrawalRequest.objects.get(user=self.user)

        self.assertEqual(
            self.profile.balance,
            Decimal("200.00"),
        )
        self.assertEqual(
            self.profile.reserved_balance,
            Decimal("50.00"),
        )
        self.assertEqual(
            withdrawal.amount,
            Decimal("50.00"),
        )
        self.assertEqual(withdrawal.status, "pending")

    def test_withdrawal_cannot_exceed_available_balance(self):
        self.profile.reserved_balance = Decimal("175.00")
        self.profile.save(update_fields=["reserved_balance"])

        response = self.client.post(
            reverse("request_withdrawal"),
            self.withdrawal_data("50.00"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            WithdrawalRequest.objects.filter(user=self.user).count(),
            0,
        )

        self.profile.refresh_from_db()
        self.assertEqual(
            self.profile.reserved_balance,
            Decimal("175.00"),
        )

    def test_minimum_withdrawal_is_50(self):
        response = self.client.post(
            reverse("request_withdrawal"),
            self.withdrawal_data("49.99"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            WithdrawalRequest.objects.filter(user=self.user).count(),
            0,
        )

        self.profile.refresh_from_db()
        self.assertEqual(
            self.profile.reserved_balance,
            Decimal("0.00"),
        )

    def test_available_balance_uses_reserved_balance(self):
        self.profile.reserved_balance = Decimal("75.00")
        self.profile.save(update_fields=["reserved_balance"])

        response = self.client.get(reverse("wallet"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["available_balance"],
            Decimal("125.00"),
        )


    def test_nan_withdrawal_is_rejected(self):
        response = self.client.post(
            reverse("request_withdrawal"),
            self.withdrawal_data("NaN"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            WithdrawalRequest.objects.filter(user=self.user).count(),
            0,
        )

        self.profile.refresh_from_db()
        self.assertEqual(
            self.profile.reserved_balance,
            Decimal("0.00"),
        )

    def test_infinity_withdrawal_is_rejected(self):
        response = self.client.post(
            reverse("request_withdrawal"),
            self.withdrawal_data("Infinity"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            WithdrawalRequest.objects.filter(user=self.user).count(),
            0,
        )

        self.profile.refresh_from_db()
        self.assertEqual(
            self.profile.reserved_balance,
            Decimal("0.00"),
        )

    def test_withdrawal_rejects_more_than_two_decimal_places(self):
        response = self.client.post(
            reverse("request_withdrawal"),
            self.withdrawal_data("50.001"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            WithdrawalRequest.objects.filter(user=self.user).count(),
            0,
        )

        self.profile.refresh_from_db()
        self.assertEqual(
            self.profile.reserved_balance,
            Decimal("0.00"),
        )


    def test_zero_withdrawal_is_rejected(self):
        response = self.client.post(
            reverse("request_withdrawal"),
            self.withdrawal_data("0"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            WithdrawalRequest.objects.filter(user=self.user).count(),
            0,
        )

        self.profile.refresh_from_db()
        self.assertEqual(
            self.profile.reserved_balance,
            Decimal("0.00"),
        )

    def test_negative_withdrawal_is_rejected(self):
        response = self.client.post(
            reverse("request_withdrawal"),
            self.withdrawal_data("-50.00"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            WithdrawalRequest.objects.filter(user=self.user).count(),
            0,
        )

        self.profile.refresh_from_db()
        self.assertEqual(
            self.profile.reserved_balance,
            Decimal("0.00"),
        )

    def test_empty_withdrawal_is_rejected(self):
        response = self.client.post(
            reverse("request_withdrawal"),
            self.withdrawal_data(""),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            WithdrawalRequest.objects.filter(user=self.user).count(),
            0,
        )

        self.profile.refresh_from_db()
        self.assertEqual(
            self.profile.reserved_balance,
            Decimal("0.00"),
        )

    def test_non_numeric_withdrawal_is_rejected(self):
        response = self.client.post(
            reverse("request_withdrawal"),
            self.withdrawal_data("abc"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            WithdrawalRequest.objects.filter(user=self.user).count(),
            0,
        )

        self.profile.refresh_from_db()
        self.assertEqual(
            self.profile.reserved_balance,
            Decimal("0.00"),
        )


class WithdrawalModelTests(TestCase):
    def test_withdrawal_defaults_to_pending(self):
        user = User.objects.create_user(username="withdrawal_user")

        withdrawal = WithdrawalRequest.objects.create(
            user=user,
            amount=Decimal("50.00"),
            bank_name="Test Bank",
            account_holder="Test Worker",
            bank_account="1234567890",
        )

        self.assertEqual(withdrawal.status, "pending")


class WithdrawalAdminActionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="admin_flow_worker",
            password="test-password-123",
        )
        self.profile = WorkerProfile.objects.create(
            user=self.user,
            balance=Decimal("200.00"),
            reserved_balance=Decimal("50.00"),
            total_earned=Decimal("200.00"),
        )

        class ModelAdminStub:
            def message_user(self, request, message, level=None):
                pass

        self.modeladmin = ModelAdminStub()
        self.request = object()

    def create_withdrawal(self, status="pending", amount="50.00"):
        return WithdrawalRequest.objects.create(
            user=self.user,
            amount=Decimal(amount),
            bank_name="Test Bank",
            account_holder="Test Worker",
            bank_account="1234567890",
            status=status,
        )

    def test_approve_withdrawal_keeps_reservation(self):
        withdrawal = self.create_withdrawal()

        approve_withdrawals(
            self.modeladmin,
            self.request,
            WithdrawalRequest.objects.filter(pk=withdrawal.pk),
        )

        withdrawal.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertEqual(withdrawal.status, "approved")
        self.assertEqual(self.profile.reserved_balance, Decimal("50.00"))
        self.assertEqual(self.profile.balance, Decimal("200.00"))

    def test_approve_withdrawal_requires_reserved_balance(self):
        self.profile.reserved_balance = Decimal("0.00")
        self.profile.save(update_fields=["reserved_balance"])

        withdrawal = self.create_withdrawal()

        approve_withdrawals(
            self.modeladmin,
            self.request,
            WithdrawalRequest.objects.filter(pk=withdrawal.pk),
        )

        withdrawal.refresh_from_db()
        self.assertEqual(withdrawal.status, "pending")

    def test_reject_withdrawal_releases_reservation(self):
        withdrawal = self.create_withdrawal()

        reject_withdrawals(
            self.modeladmin,
            self.request,
            WithdrawalRequest.objects.filter(pk=withdrawal.pk),
        )

        withdrawal.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertEqual(withdrawal.status, "rejected")
        self.assertEqual(self.profile.reserved_balance, Decimal("0.00"))
        self.assertEqual(self.profile.balance, Decimal("200.00"))

    def test_paid_withdrawal_deducts_balance_and_reservation(self):
        withdrawal = self.create_withdrawal(status="approved")

        mark_withdrawals_paid(
            self.modeladmin,
            self.request,
            WithdrawalRequest.objects.filter(pk=withdrawal.pk),
        )

        withdrawal.refresh_from_db()
        self.profile.refresh_from_db()

        transaction = WalletTransaction.objects.get(
            user=self.user,
            transaction_type="withdrawal",
        )

        self.assertEqual(withdrawal.status, "paid")
        self.assertEqual(self.profile.balance, Decimal("150.00"))
        self.assertEqual(self.profile.reserved_balance, Decimal("0.00"))
        self.assertEqual(transaction.amount, Decimal("50.00"))
        self.assertEqual(
            transaction.description,
            f"Withdrawal #{withdrawal.id}",
        )

    def test_paid_withdrawal_is_idempotent(self):
        withdrawal = self.create_withdrawal(status="approved")

        mark_withdrawals_paid(
            self.modeladmin,
            self.request,
            WithdrawalRequest.objects.filter(pk=withdrawal.pk),
        )

        self.profile.refresh_from_db()
        first_balance = self.profile.balance
        first_reserved = self.profile.reserved_balance
        first_transactions = WalletTransaction.objects.filter(
            user=self.user,
            transaction_type="withdrawal",
        ).count()

        mark_withdrawals_paid(
            self.modeladmin,
            self.request,
            WithdrawalRequest.objects.filter(pk=withdrawal.pk),
        )

        self.profile.refresh_from_db()

        self.assertEqual(self.profile.balance, first_balance)
        self.assertEqual(self.profile.reserved_balance, first_reserved)
        self.assertEqual(
            WalletTransaction.objects.filter(
                user=self.user,
                transaction_type="withdrawal",
            ).count(),
            first_transactions,
        )

    def test_paid_withdrawal_with_existing_matching_transaction_is_completed(self):
        withdrawal = self.create_withdrawal(status="approved")

        WalletTransaction.objects.create(
            user=self.user,
            amount=withdrawal.amount,
            transaction_type="withdrawal",
            description=f"Withdrawal #{withdrawal.id}",
        )

        mark_withdrawals_paid(
            self.modeladmin,
            self.request,
            WithdrawalRequest.objects.filter(pk=withdrawal.pk),
        )

        withdrawal.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertEqual(withdrawal.status, "paid")
        self.assertEqual(self.profile.balance, Decimal("200.00"))
        self.assertEqual(self.profile.reserved_balance, Decimal("0.00"))
        self.assertEqual(
            WalletTransaction.objects.filter(
                user=self.user,
                transaction_type="withdrawal",
            ).count(),
            1,
        )

    def test_reject_withdrawal_without_reservation_keeps_pending(self):
        self.profile.reserved_balance = Decimal("0.00")
        self.profile.save(update_fields=["reserved_balance"])

        withdrawal = self.create_withdrawal()

        reject_withdrawals(
            self.modeladmin,
            self.request,
            WithdrawalRequest.objects.filter(pk=withdrawal.pk),
        )

        withdrawal.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertEqual(withdrawal.status, "pending")
        self.assertEqual(
            self.profile.reserved_balance,
            Decimal("0.00"),
        )

    def test_paid_withdrawal_without_reservation_stays_approved(self):
        self.profile.reserved_balance = Decimal("0.00")
        self.profile.save(update_fields=["reserved_balance"])

        withdrawal = self.create_withdrawal(status="approved")

        mark_withdrawals_paid(
            self.modeladmin,
            self.request,
            WithdrawalRequest.objects.filter(pk=withdrawal.pk),
        )

        withdrawal.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertEqual(withdrawal.status, "approved")
        self.assertEqual(
            self.profile.balance,
            Decimal("200.00"),
        )
        self.assertEqual(
            self.profile.reserved_balance,
            Decimal("0.00"),
        )
        self.assertEqual(
            WalletTransaction.objects.filter(
                user=self.user,
                transaction_type="withdrawal",
            ).count(),
            0,
        )

    def test_paid_withdrawal_without_enough_balance_stays_approved(self):
        self.profile.balance = Decimal("40.00")
        self.profile.reserved_balance = Decimal("50.00")
        self.profile.save(
            update_fields=["balance", "reserved_balance"]
        )

        withdrawal = self.create_withdrawal(status="approved")

        mark_withdrawals_paid(
            self.modeladmin,
            self.request,
            WithdrawalRequest.objects.filter(pk=withdrawal.pk),
        )

        withdrawal.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertEqual(withdrawal.status, "approved")
        self.assertEqual(
            self.profile.balance,
            Decimal("40.00"),
        )
        self.assertEqual(
            self.profile.reserved_balance,
            Decimal("50.00"),
        )
        self.assertEqual(
            WalletTransaction.objects.filter(
                user=self.user,
                transaction_type="withdrawal",
            ).count(),
            0,
        )

    def test_already_paid_with_wrong_amount_stays_approved(self):
        withdrawal = self.create_withdrawal(
            status="approved",
            amount="50.00",
        )

        WalletTransaction.objects.create(
            user=self.user,
            amount=Decimal("40.00"),
            transaction_type="withdrawal",
            description=f"Withdrawal #{withdrawal.id}",
        )

        mark_withdrawals_paid(
            self.modeladmin,
            self.request,
            WithdrawalRequest.objects.filter(pk=withdrawal.pk),
        )

        withdrawal.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertEqual(withdrawal.status, "approved")
        self.assertEqual(
            self.profile.balance,
            Decimal("200.00"),
        )
        self.assertEqual(
            self.profile.reserved_balance,
            Decimal("50.00"),
        )
