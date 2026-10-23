from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import AccountEntity
from promotions.models import Promotion, PromotionClaim


class PromotionSubmissionMethodBoundaryTests(TestCase):
    def setUp(self):
        self.worker = get_user_model().objects.create_user(
            username="promotion_method_worker",
            password="StrongTestPass123!",
        )
        AccountEntity.objects.create(
            user=self.worker,
            entity_type=AccountEntity.EntityType.WORKER,
        )
        self.promotion = Promotion.objects.create(
            title="Method boundary promotion",
            description="Synthetic test promotion",
            advertiser_name="Test Advertiser",
            reward="10.00",
            budget="20.00",
            max_workers=1,
            status="approved",
        )
        self.claim = PromotionClaim.objects.create(
            promotion=self.promotion,
            worker=self.worker,
            status="claimed",
        )
        self.client.force_login(self.worker)

    def test_put_is_rejected_without_changing_claim_or_proof(self):
        response = self.client.put(
            reverse("submit_promotion", args=[self.promotion.pk]),
            data={"proof": "must not be accepted"},
        )

        self.assertEqual(response.status_code, 405)
        self.claim.refresh_from_db()
        self.assertEqual(self.claim.status, "claimed")
        self.assertEqual(self.claim.proof, "")
        self.assertIsNone(self.claim.submitted_at)
