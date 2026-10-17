"""PostgreSQL-only concurrency coverage for promotion cumulative budget safety.

SQLite does not implement SELECT FOR UPDATE with PostgreSQL semantics, so this
test is deliberately skipped there. The PostgreSQL CI workflow runs the full
suite and must execute this test.
"""
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from threading import Barrier
from unittest.mock import patch

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import close_old_connections, connection
from django.db.models import Sum
from django.test import RequestFactory, TransactionTestCase, skipUnlessDBFeature

from accounts.models import AccountEntity, WorkerProfile
from wallet.models import WalletTransaction
from .admin import PromotionClaimAdmin
from .models import Promotion, PromotionClaim


@skipUnlessDBFeature("has_select_for_update")
class PromotionBudgetConcurrencyTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        if connection.vendor != "postgresql":
            self.skipTest("Requires PostgreSQL row-lock semantics")

        User = get_user_model()
        self.admin_user = User.objects.create_superuser(
            username="budget_concurrency_admin",
            email="budget-admin@example.test",
            password="test-only-password",
        )
        self.workers = []
        self.claims = []
        for index in range(2):
            worker = User.objects.create_user(
                username=f"budget_concurrency_worker_{index}",
                password="test-only-password",
            )
            AccountEntity.objects.create(
                user=worker,
                entity_type=AccountEntity.EntityType.WORKER,
            )
            WorkerProfile.objects.create(
                user=worker,
                balance=Decimal("0.00"),
                reserved_balance=Decimal("0.00"),
                total_earned=Decimal("0.00"),
            )
            self.workers.append(worker)

        self.promotion = Promotion.objects.create(
            title="Concurrent budget boundary",
            description="Synthetic concurrency test",
            advertiser_name="Synthetic advertiser",
            reward=Decimal("60.00"),
            budget=Decimal("100.00"),
            max_workers=2,
            reserved_workers=2,
            completed_workers=0,
            status="paused",
        )
        for worker in self.workers:
            self.claims.append(
                PromotionClaim.objects.create(
                    promotion=self.promotion,
                    worker=worker,
                    status="submitted",
                )
            )

    def _approve_one(self, claim_id, barrier):
        close_old_connections()
        try:
            barrier.wait(timeout=10)
            User = get_user_model()
            actor = User.objects.get(pk=self.admin_user.pk)
            request = RequestFactory().post("/admin/promotions/promotionclaim/")
            request.user = actor
            model_admin = PromotionClaimAdmin(PromotionClaim, admin.site)
            model_admin.message_user = lambda *args, **kwargs: None
            with patch("promotions.admin.require_execution_authorized"):
                model_admin.approve_claims(
                    request,
                    PromotionClaim.objects.filter(pk=claim_id),
                )
            return "ok"
        finally:
            close_old_connections()

    def test_competing_approvals_cannot_exceed_cumulative_budget(self):
        barrier = Barrier(2)
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [
                pool.submit(self._approve_one, claim.pk, barrier)
                for claim in self.claims
            ]
            outcomes = [future.result(timeout=30) for future in futures]

        self.assertEqual(outcomes, ["ok", "ok"])
        approved_claims = PromotionClaim.objects.filter(
            promotion=self.promotion,
            status="approved",
        ).count()
        self.assertEqual(approved_claims, 1)

        earning_rows = WalletTransaction.objects.filter(
            promotion_claim__promotion=self.promotion,
            transaction_type="earning",
        )
        self.assertEqual(earning_rows.count(), 1)
        total_paid = earning_rows.aggregate(total=Sum("amount"))["total"]
        self.assertEqual(total_paid, Decimal("60.00"))
        self.promotion.refresh_from_db()
        self.assertEqual(self.promotion.completed_workers, 1)
