from decimal import Decimal

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase

from accounts.models import AccountEntity, WorkerProfile
from promotions.admin import PromotionClaimAdmin
from promotions.models import Promotion, PromotionClaim
from wallet.models import WalletTransaction


class PromotionPayoutIntegrityTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_superuser(
            username="promotion-owner",
            password="Strong-Test-Password-123!",
            email="owner@example.test",
        )
        AccountEntity.objects.create(
            user=self.owner,
            entity_type=AccountEntity.EntityType.OWNER,
        )
        self.worker = User.objects.create_user(
            username="promotion-payout-worker",
            password="Strong-Test-Password-123!",
        )
        AccountEntity.objects.create(
            user=self.worker,
            entity_type=AccountEntity.EntityType.WORKER,
        )
        WorkerProfile.objects.create(user=self.worker)
        self.promotion = Promotion.objects.create(
            title="Payout Integrity Promotion",
            description="Payout test",
            advertiser_name="Test Advertiser",
            reward=Decimal("10.00"),
            budget=Decimal("10.00"),
            max_workers=1,
            completed_workers=0,
            status="active",
        )
        self.claim = PromotionClaim.objects.create(
            promotion=self.promotion,
            worker=self.worker,
            status="submitted",
            proof="proof",
        )

    def test_approval_pays_once_and_marks_completion(self):
        request = RequestFactory().post("/admin/promotions/promotionclaim/")
        request.user = self.owner
        request.session = self.client.session
        request._messages = FallbackStorage(request)

        modeladmin = PromotionClaimAdmin(
            PromotionClaim,
            admin.site,
        )
        modeladmin.approve_claims(request, PromotionClaim.objects.filter(pk=self.claim.pk))

        self.claim.refresh_from_db()
        self.promotion.refresh_from_db()
        profile = WorkerProfile.objects.get(user=self.worker)

        self.assertEqual(self.claim.status, "approved")
        self.assertEqual(self.promotion.completed_workers, 1)
        self.assertEqual(self.promotion.status, "paused")
        self.assertEqual(profile.balance, Decimal("10.00"))
        self.assertEqual(
            WalletTransaction.objects.filter(
                promotion_claim=self.claim,
                transaction_type="earning",
            ).count(),
            1,
        )

        modeladmin.approve_claims(request, PromotionClaim.objects.filter(pk=self.claim.pk))
        self.assertEqual(
            WalletTransaction.objects.filter(
                promotion_claim=self.claim,
                transaction_type="earning",
            ).count(),
            1,
        )
