from decimal import Decimal
from unittest.mock import patch

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import AccountEntity, WorkerProfile
from wallet.models import WalletTransaction
from .admin import PromotionClaimAdmin
from .models import Promotion, PromotionClaim


class PromotionClaimWorkflowReconciliationTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="promotion_workflow_worker",
            password="test-password-123",
        )
        AccountEntity.objects.create(
            user=self.user, entity_type=AccountEntity.EntityType.WORKER
        )
        WorkerProfile.objects.create(
            user=self.user,
            balance=Decimal("100.00"),
            reserved_balance=Decimal("0.00"),
            total_earned=Decimal("100.00"),
        )
        self.admin_user = User.objects.create_superuser(
            username="promotion_workflow_admin", password="test-admin-password"
        )
        self.promotion = Promotion.objects.create(
            title="Workflow Promotion", description="Test", advertiser_name="Advertiser",
            reward=Decimal("25.00"), budget=Decimal("100.00"), max_workers=1,
            reserved_workers=1, completed_workers=0, status="paused",
        )
        self.claim = PromotionClaim.objects.create(
            promotion=self.promotion, worker=self.user, status="submitted"
        )

    def request(self):
        request = type("RequestStub", (), {})()
        request.user = self.admin_user
        return request

    def test_new_approval_increments_completed_once_and_pays(self):
        model_admin = PromotionClaimAdmin(PromotionClaim, admin.site)
        with patch("promotions.admin.require_execution_authorized"):
            model_admin.approve_claims(self.request(), PromotionClaim.objects.filter(pk=self.claim.pk))
        self.claim.refresh_from_db(); self.promotion.refresh_from_db()
        self.assertEqual(self.claim.status, "approved")
        self.assertEqual(self.promotion.completed_workers, 1)
        self.assertEqual(self.promotion.reserved_workers, 1)
        self.assertEqual(WalletTransaction.objects.filter(promotion_claim=self.claim, transaction_type="earning").count(), 1)

    def test_existing_ledger_reconciliation_increments_completed_without_double_payment(self):
        WalletTransaction.objects.create(
            user=self.user, amount=Decimal("25.00"), transaction_type="earning",
            description="Existing promotion reward", promotion_claim=self.claim,
        )
        model_admin = PromotionClaimAdmin(PromotionClaim, admin.site)
        with patch("promotions.admin.require_execution_authorized"):
            model_admin.approve_claims(self.request(), PromotionClaim.objects.filter(pk=self.claim.pk))
        self.claim.refresh_from_db(); self.promotion.refresh_from_db()
        self.assertEqual(self.claim.status, "approved")
        self.assertEqual(self.promotion.completed_workers, 1)
        self.assertEqual(WalletTransaction.objects.filter(promotion_claim=self.claim, transaction_type="earning").count(), 1)
        self.assertEqual(WorkerProfile.objects.get(user=self.user).balance, Decimal("100.00"))

    def test_rejection_releases_reservation_and_reopens_paused_promotion(self):
        model_admin = PromotionClaimAdmin(PromotionClaim, admin.site)
        with patch("promotions.admin.require_execution_authorized"):
            model_admin.reject_claims(self.request(), PromotionClaim.objects.filter(pk=self.claim.pk))
        self.claim.refresh_from_db(); self.promotion.refresh_from_db()
        self.assertEqual(self.claim.status, "rejected")
        self.assertEqual(self.promotion.reserved_workers, 0)
        self.assertEqual(self.promotion.completed_workers, 0)
        self.assertEqual(self.promotion.status, "active")

    def test_approved_replay_does_not_double_count_or_pay(self):
        model_admin = PromotionClaimAdmin(PromotionClaim, admin.site)
        with patch("promotions.admin.require_execution_authorized"):
            model_admin.approve_claims(self.request(), PromotionClaim.objects.filter(pk=self.claim.pk))
        balance_after_first = WorkerProfile.objects.get(user=self.user).balance
        with patch("promotions.admin.require_execution_authorized"):
            model_admin.approve_claims(self.request(), PromotionClaim.objects.filter(pk=self.claim.pk))
        self.promotion.refresh_from_db()
        self.assertEqual(self.promotion.completed_workers, 1)
        self.assertEqual(WalletTransaction.objects.filter(promotion_claim=self.claim, transaction_type="earning").count(), 1)
        self.assertEqual(WorkerProfile.objects.get(user=self.user).balance, balance_after_first)
