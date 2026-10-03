from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import AccountEntity, WorkerProfile
from promotions.models import Promotion, PromotionClaim


class PromotionLifecycleIntegrityTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.worker = User.objects.create_user(
            username="promotion-worker",
            password="Strong-Test-Password-123!",
        )
        AccountEntity.objects.create(
            user=self.worker,
            entity_type=AccountEntity.EntityType.WORKER,
        )
        WorkerProfile.objects.create(user=self.worker)
        self.promotion = Promotion.objects.create(
            title="Integrity Promotion",
            description="Lifecycle test",
            advertiser_name="Test Advertiser",
            reward=Decimal("10.00"),
            budget=Decimal("20.00"),
            max_workers=2,
            status="active",
        )
        self.client.force_login(self.worker)

    def test_start_does_not_mark_claim_as_completed(self):
        response = self.client.post(
            reverse(
                "start_promotion",
                kwargs={"promotion_id": self.promotion.id},
            )
        )
        self.assertEqual(response.status_code, 302)
        self.promotion.refresh_from_db()
        self.assertEqual(self.promotion.completed_workers, 0)
        self.assertEqual(
            PromotionClaim.objects.filter(
                promotion=self.promotion,
                worker=self.worker,
                status="claimed",
            ).count(),
            1,
        )

    def test_rejected_claim_can_reenter_without_inflating_completion(self):
        claim = PromotionClaim.objects.create(
            promotion=self.promotion,
            worker=self.worker,
            status="rejected",
        )
        response = self.client.post(
            reverse(
                "start_promotion",
                kwargs={"promotion_id": self.promotion.id},
            )
        )
        self.assertEqual(response.status_code, 302)
        claim.refresh_from_db()
        self.promotion.refresh_from_db()
        self.assertEqual(claim.status, "claimed")
        self.assertEqual(self.promotion.completed_workers, 0)
