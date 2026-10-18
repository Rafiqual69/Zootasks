from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import connections
from django.test import Client, TransactionTestCase, skipUnlessDBFeature
from django.urls import reverse

from accounts.models import AccountEntity
from promotions.models import Promotion, PromotionClaim


@skipUnlessDBFeature("has_select_for_update")
class PromotionLastSlotConcurrencyTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        User = get_user_model()
        self.clients = []
        for index in range(2):
            user = User.objects.create_user(
                username=f"promotion_race_worker_{index}",
                password="test-password-123",
            )
            AccountEntity.objects.create(
                user=user,
                entity_type=AccountEntity.EntityType.WORKER,
                is_active=True,
            )
            client = Client()
            client.force_login(user)
            self.clients.append(client)

        self.promotion = Promotion.objects.create(
            title="Single Slot Race",
            description="PostgreSQL concurrency regression",
            advertiser_name="Test Advertiser",
            reward="10.00",
            budget="10.00",
            max_workers=1,
            reserved_workers=0,
            completed_workers=0,
            status="active",
        )

    @patch("promotions.views.require_authorized")
    def test_two_workers_cannot_reserve_the_same_last_slot(self, authorize):
        barrier = Barrier(2)
        url = reverse("start_promotion", args=[self.promotion.pk])

        def submit_claim(client):
            # Force-close thread-local persistent connections so the test DB can
            # be safely dropped by Django's test runner after the test.
            connections.close_all()
            try:
                barrier.wait(timeout=10)
                return client.post(url)
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=2) as pool:
            responses = list(pool.map(submit_claim, self.clients))

        self.promotion.refresh_from_db()
        self.assertLessEqual(self.promotion.reserved_workers, self.promotion.max_workers)
        self.assertEqual(self.promotion.reserved_workers, 1)
        self.assertEqual(
            PromotionClaim.objects.filter(promotion=self.promotion).count(),
            1,
        )
        self.assertEqual(self.promotion.status, "paused")
        self.assertEqual(sorted(response.status_code for response in responses), [302, 404])
