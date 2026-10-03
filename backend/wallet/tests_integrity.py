from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import AccountEntity, WorkerProfile
from wallet.models import WithdrawalRequest


class WithdrawalIntegrityTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.worker = User.objects.create_user(
            username="withdrawal-worker",
            password="Strong-Test-Password-123!",
        )
        AccountEntity.objects.create(
            user=self.worker,
            entity_type=AccountEntity.EntityType.WORKER,
        )
        self.profile = WorkerProfile.objects.create(
            user=self.worker,
            balance=Decimal("100.00"),
            reserved_balance=Decimal("0.00"),
        )
        self.client.force_login(self.worker)

    def test_insufficient_withdrawal_does_not_redirect_or_reserve(self):
        response = self.client.post(
            reverse("request_withdrawal"),
            {
                "amount": "150.00",
                "bank_name": "Test Bank",
                "account_holder": "Test Worker",
                "bank_account": "0001",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WithdrawalRequest.objects.count(), 0)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.reserved_balance, Decimal("0.00"))

    def test_valid_withdrawal_reserves_balance_once(self):
        response = self.client.post(
            reverse("request_withdrawal"),
            {
                "amount": "50.00",
                "bank_name": "Test Bank",
                "account_holder": "Test Worker",
                "bank_account": "0001",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("withdrawal_success"))
        self.assertEqual(WithdrawalRequest.objects.count(), 1)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.reserved_balance, Decimal("50.00"))
