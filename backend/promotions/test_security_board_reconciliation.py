from decimal import Decimal
from unittest.mock import patch

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import WorkerProfile
from promotions.admin import PromotionClaimAdmin
from promotions.models import Promotion, PromotionClaim
from wallet.models import WalletTransaction


class PromotionReconciliationRegressionTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.worker = User.objects.create_user(
            username="promotion_reconcile_worker",
            password="test-password-123",
        )
        WorkerProfile.objects.create(
            user=self.worker,
            balance=Decimal("100.00"),
            reserved_balance=Decimal("0.00"),
            total_earned=Decimal("100.00"),
        )
        self.operator = User.objects.create_superuser(
            username="promotion_reconcile_operator",
            password="test-password-123",
        )
        self.request = type("RequestStub", (), {})()
        self.request.user = self.operator
        self.modeladmin = PromotionClaimAdmin(PromotionClaim, admin.site)

    def make_promotion(self, **overrides):
        values = {
            "title": "Reconciliation regression",
            "description": "Regression test",
            "advertiser_name": "Test advertiser",
            "reward": Decimal("25.00"),
            "budget": Decimal("100.00"),
            "max_workers": 1,
            "reserved_workers": 1,
            "completed_workers": 0,
            "status": "paused",
        }
        values.update(overrides)
        return Promotion.objects.create(**values)

    def make_submitted_claim(self, promotion):
        return PromotionClaim.objects.create(
            promotion=promotion,
            worker=self.worker,
            status="submitted",
        )

    @patch("promotions.admin.require_execution_authorized")
    def test_matching_legacy_ledger_reconciles_completion_without_second_credit(
        self, authorize_execution
    ):
        promotion = self.make_promotion()
        claim = self.make_submitted_claim(promotion)
        WalletTransaction.objects.create(
            user=self.worker,
            amount=Decimal("25.00"),
            transaction_type="earning",
            description="Legacy promotion payment",
            promotion_claim=claim,
        )

        with patch.object(self.modeladmin, "message_user"):
            self.modeladmin.approve_claims(
                self.request, PromotionClaim.objects.filter(pk=claim.pk)
            )

        claim.refresh_from_db()
        promotion.refresh_from_db()
        profile = WorkerProfile.objects.get(user=self.worker)

        self.assertEqual(claim.status, "approved")
        self.assertEqual(promotion.completed_workers, 1)
        self.assertEqual(profile.balance, Decimal("100.00"))
        self.assertEqual(profile.total_earned, Decimal("100.00"))
        self.assertEqual(
            WalletTransaction.objects.filter(
                promotion_claim=claim,
                transaction_type="earning",
            ).count(),
            1,
        )
        authorize_execution.assert_called_once()

        # Replaying the same approval action must not increment completion or pay again.
        with patch.object(self.modeladmin, "message_user"):
            self.modeladmin.approve_claims(
                self.request, PromotionClaim.objects.filter(pk=claim.pk)
            )

        promotion.refresh_from_db()
        self.assertEqual(promotion.completed_workers, 1)
        self.assertEqual(
            WalletTransaction.objects.filter(
                promotion_claim=claim,
                transaction_type="earning",
            ).count(),
            1,
        )

    @patch("promotions.admin.require_execution_authorized")
    def test_rejection_replay_releases_capacity_once_and_reopens_full_promotion(
        self, authorize_execution
    ):
        promotion = self.make_promotion()
        claim = self.make_submitted_claim(promotion)

        with patch.object(self.modeladmin, "message_user"):
            self.modeladmin.reject_claims(
                self.request, PromotionClaim.objects.filter(pk=claim.pk)
            )

        claim.refresh_from_db()
        promotion.refresh_from_db()
        self.assertEqual(claim.status, "rejected")
        self.assertEqual(promotion.reserved_workers, 0)
        self.assertEqual(promotion.completed_workers, 0)
        self.assertEqual(promotion.status, "active")
        authorize_execution.assert_called_once()

        # Replaying rejection must not decrement capacity below zero.
        with patch.object(self.modeladmin, "message_user"):
            self.modeladmin.reject_claims(
                self.request, PromotionClaim.objects.filter(pk=claim.pk)
            )

        claim.refresh_from_db()
        promotion.refresh_from_db()
        self.assertEqual(claim.status, "rejected")
        self.assertEqual(promotion.reserved_workers, 0)
        self.assertEqual(promotion.completed_workers, 0)
        self.assertEqual(promotion.status, "active")
        authorize_execution.assert_called_once()
