from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import AccountEntity
from tasks.models import Task, TaskClaim


class TaskSubmissionMethodBoundaryTests(TestCase):
    def setUp(self):
        self.worker = User.objects.create_user(
            username="method_worker",
            password="StrongTestPass123!",
        )
        AccountEntity.objects.create(
            user=self.worker,
            entity_type=AccountEntity.EntityType.WORKER,
        )
        self.task = Task.objects.create(
            title="Method boundary task",
            description="Synthetic test task",
            category="Testing",
            reward="10.00",
            max_workers=1,
        )
        self.claim = TaskClaim.objects.create(
            task=self.task,
            worker=self.worker,
            status="claimed",
        )
        self.client.force_login(self.worker)

    def test_put_is_rejected_without_changing_claim_or_proof(self):
        response = self.client.put(
            reverse("submit_task", args=[self.task.pk]),
            data={"proof": "must not be accepted"},
        )

        self.assertEqual(response.status_code, 405)
        self.claim.refresh_from_db()
        self.assertEqual(self.claim.status, "claimed")
        self.assertEqual(self.claim.proof, "")
        self.assertIsNone(self.claim.submitted_at)
