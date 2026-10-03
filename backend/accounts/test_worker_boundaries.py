from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import AccountEntity, AdvertiserProfile
from promotions.models import Promotion
from tasks.models import Task
from tasks.services import TaskServiceError, claim_task_for_worker


class WorkerAuthorizationBoundaryTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.advertiser = User.objects.create_user(
            username="boundary-advertiser",
            password="StrongTestPass123!",
        )
        AccountEntity.objects.create(
            user=self.advertiser,
            entity_type=AccountEntity.EntityType.ADVERTISER,
            identity_email="boundary@example.com",
        )
        AdvertiserProfile.objects.create(
            user=self.advertiser,
            organization_name="Boundary Co",
        )
        self.task = Task.objects.create(
            title="Boundary Task",
            description="Worker-only task.",
            reward=Decimal("10.00"),
            max_workers=1,
        )
        self.promotion = Promotion.objects.create(
            title="Boundary Promotion",
            description="Worker-only promotion.",
            advertiser_name="Boundary Co",
            advertiser=self.advertiser.advertiser_profile,
            reward=Decimal("5.00"),
            budget=Decimal("5.00"),
            max_workers=1,
            status="active",
        )

    def test_non_worker_cannot_claim_task_at_service_boundary(self):
        with self.assertRaises(TaskServiceError) as exc:
            claim_task_for_worker(
                user=self.advertiser,
                task_id=self.task.id,
            )

        self.assertEqual(str(exc.exception), "worker_access_required")
        self.assertEqual(self.task.claims.count(), 0)
        self.task.refresh_from_db()
        self.assertEqual(self.task.claimed_workers, 0)

    def test_non_worker_cannot_start_promotion(self):
        self.client.force_login(self.advertiser)
        response = self.client.post(
            reverse("start_promotion", args=[self.promotion.id])
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.promotion.claims.count(), 0)
        self.promotion.refresh_from_db()
        self.assertEqual(self.promotion.completed_workers, 0)

    def test_non_worker_cannot_access_wallet(self):
        self.client.force_login(self.advertiser)
        response = self.client.get(reverse("wallet"))

        self.assertEqual(response.status_code, 403)
