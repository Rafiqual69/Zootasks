from decimal import Decimal

from django.db import IntegrityError
from django.test import TestCase

from .models import Promotion


class PromotionFinancialInvariantTests(TestCase):
    def test_negative_reward_is_rejected(self):
        with self.assertRaises(IntegrityError):
            Promotion.objects.create(
                title="Negative reward",
                description="Must be rejected",
                advertiser_name="Test",
                reward=Decimal("-1.00"),
                budget=Decimal("10.00"),
                max_workers=1,
            )

    def test_negative_budget_is_rejected(self):
        with self.assertRaises(IntegrityError):
            Promotion.objects.create(
                title="Negative budget",
                description="Must be rejected",
                advertiser_name="Test",
                reward=Decimal("1.00"),
                budget=Decimal("-1.00"),
                max_workers=1,
            )

    def test_completed_workers_cannot_exceed_capacity(self):
        with self.assertRaises(IntegrityError):
            Promotion.objects.create(
                title="Over capacity",
                description="Must be rejected",
                advertiser_name="Test",
                reward=Decimal("10.00"),
                budget=Decimal("100.00"),
                max_workers=1,
                completed_workers=2,
            )
