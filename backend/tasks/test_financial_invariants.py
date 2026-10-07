from decimal import Decimal

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase

from .models import Task


class TaskFinancialInvariantTests(TestCase):
    def test_negative_reward_is_rejected(self):
        with self.assertRaises(IntegrityError):
            Task.objects.create(
                title="Negative reward",
                description="Must be rejected",
                reward=Decimal("-1.00"),
                max_workers=1,
            )

    def test_completed_workers_cannot_exceed_capacity(self):
        with self.assertRaises(IntegrityError):
            Task.objects.create(
                title="Over capacity",
                description="Must be rejected",
                reward=Decimal("10.00"),
                max_workers=1,
                completed_workers=2,
            )
