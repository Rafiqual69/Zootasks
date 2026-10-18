from decimal import Decimal
from unittest.mock import patch

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import RequestFactory, TestCase

from accounts.models import WorkerProfile
from wallet.models import WalletTransaction
from .admin import PromotionClaimAdmin
from .models import Promotion, PromotionClaim


class PromotionClaimTransitionRegressionTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.worker = User.objects.create_user(
            username="promotion_transition_worker",
            password="test-password-123",
        )
        WorkerProfile.objects.create(
            user=self.worker,
            balance=Decimal("0.00"),
            reserved_balance=Decimal("0.00"),
            total_earned=Decimal("0.00"),
        )
        self.promotion = Promotion.objects.create(
            title="Transition Promotion",
            description="Regression test",
            advertiser_name="Test Advertiser",
            reward=Decimal("25.00"),
            budget=Decimal("100.00"),
            max_workers=1,
            reserved_workers=1,
            completed_workers=0,
            status="paused",
        )
        self.claim = PromotionClaim.objects.create(
            promotion=self.promotion,
            worker=self.worker,
            status="submitted",
        )

        self.reviewer = User.objects.create_user(
            username="promotion_transition_reviewer",
            password="test-password-123",
            is_staff=True,
        )
        self.reviewer.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="promotions",
                codename="approve_promotion_claim",
            ),
            Permission.objects.get(
                content_type__app_label="promotions",
                codename="reject_promotion_claim",
            ),
        )
        self.request = RequestFactory().post("/admin/promotions/promotionclaim/")
        self.request.user = self.reviewer
        self.model_admin = PromotionClaimAdmin(PromotionClaim, admin.site)

    @patch("promotions.admin.require_execution_authorized")
    def test_approval_credits_and_completes_once_even_when_action_replayed(
        self, authorize_execution
    ):
        queryset = PromotionClaim.objects.filter(pk=self.claim.pk)

        with patch.object(self.model_admin, "message_user"):
            self.model_admin.approve_claims(self.request, queryset)
            self.model_admin.approve_claims(self.request, queryset)

        self.claim.refresh_from_db()
        self.promotion.refresh_from_db()
        self.worker_profile = WorkerProfile.objects.get(user=self.worker)

        self.assertEqual(self.claim.status, "approved")
        self.assertEqual(self.promotion.reserved_workers, 1)
        self.assertEqual(self.promotion.completed_workers, 1)
        self.assertEqual(self.worker_profile.balance, Decimal("25.00"))
        self.assertEqual(self.worker_profile.total_earned, Decimal("25.00"))
        self.assertEqual(
            WalletTransaction.objects.filter(
                promotion_claim=self.claim,
                transaction_type="earning",
            ).count(),
            1,
        )
        authorize_execution.assert_called_once()

    @patch("promotions.admin.require_execution_authorized")
    def test_existing_ledger_reconciliation_approves_without_duplicate_credit(
        self, authorize_execution
    ):
        WalletTransaction.objects.create(
            user=self.worker,
            amount=Decimal("25.00"),
            transaction_type="earning",
            description="Legacy promotion payment",
            promotion_claim=self.claim,
        )
        queryset = PromotionClaim.objects.filter(pk=self.claim.pk)

        with patch.object(self.model_admin, "message_user"):
            self.model_admin.approve_claims(self.request, queryset)
            self.model_admin.approve_claims(self.request, queryset)

        self.claim.refresh_from_db()
        self.promotion.refresh_from_db()

        self.assertEqual(self.claim.status, "approved")
        self.assertEqual(self.promotion.completed_workers, 1)
        self.assertEqual(
            WalletTransaction.objects.filter(
                promotion_claim=self.claim,
                transaction_type="earning",
            ).count(),
            1,
        )
        self.assertEqual(
            WorkerProfile.objects.get(user=self.worker).balance,
            Decimal("0.00"),
        )
        authorize_execution.assert_called_once()

    @patch("promotions.admin.require_execution_authorized")
    def test_rejection_releases_last_slot_and_replay_does_not_decrement_twice(
        self, authorize_execution
    ):
        queryset = PromotionClaim.objects.filter(pk=self.claim.pk)

        with patch.object(self.model_admin, "message_user"):
            self.model_admin.reject_claims(self.request, queryset)
            self.model_admin.reject_claims(self.request, queryset)

        self.claim.refresh_from_db()
        self.promotion.refresh_from_db()

        self.assertEqual(self.claim.status, "rejected")
        self.assertEqual(self.promotion.reserved_workers, 0)
        self.assertEqual(self.promotion.completed_workers, 0)
        self.assertEqual(self.promotion.status, "active")
        authorize_execution.assert_called_once()
