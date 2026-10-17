from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase

from .models import Promotion, PromotionClaim


class PromotionCapacityInvariantTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="promotion_invariant_worker",
            password="test-password-123",
        )

    def test_reserved_workers_cannot_exceed_max_workers(self):
        promotion = Promotion.objects.create(
            title="Invariant promotion",
            description="Test",
            advertiser_name="Test",
            reward="1.00",
            budget="10.00",
            max_workers=1,
            reserved_workers=1,
            completed_workers=0,
            status="active",
        )
        promotion.reserved_workers = 2
        with self.assertRaises(IntegrityError):
            promotion.save(update_fields=["reserved_workers"])

    def test_completed_workers_cannot_exceed_reserved_workers(self):
        promotion = Promotion.objects.create(
            title="Invariant promotion",
            description="Test",
            advertiser_name="Test",
            reward="1.00",
            budget="10.00",
            max_workers=2,
            reserved_workers=1,
            completed_workers=1,
            status="active",
        )
        promotion.completed_workers = 2
        with self.assertRaises(IntegrityError):
            promotion.save(update_fields=["completed_workers"])

    def test_rejected_claim_is_not_a_capacity_reservation(self):
        promotion = Promotion.objects.create(
            title="Invariant promotion",
            description="Test",
            advertiser_name="Test",
            reward="1.00",
            budget="10.00",
            max_workers=2,
            reserved_workers=0,
            completed_workers=0,
            status="active",
        )
        PromotionClaim.objects.create(
            promotion=promotion,
            worker=self.user,
            status="rejected",
        )
        self.assertEqual(
            promotion.claims.exclude(status="rejected").count(),
            promotion.reserved_workers,
        )
