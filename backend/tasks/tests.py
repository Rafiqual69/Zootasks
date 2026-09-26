from django.contrib import admin
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Task, TaskClaim


class TaskMarketplaceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="worker1",
            password="StrongTestPass123!",
        )
        self.other_user = User.objects.create_user(
            username="worker2",
            password="StrongTestPass123!",
        )

        self.active_task = Task.objects.create(
            title="Test Active Task",
            description="Complete this test task.",
            category="Testing",
            reward="10.00",
            max_workers=2,
        )

        self.paused_task = Task.objects.create(
            title="Paused Task",
            description="This task must not appear.",
            category="Testing",
            reward="20.00",
            max_workers=1,
            status="paused",
        )

    def login(self):
        self.client.force_login(self.user)

    def test_marketplace_requires_login(self):
        response = self.client.get(reverse("task_marketplace"))
        self.assertEqual(response.status_code, 302)

    def test_marketplace_shows_active_tasks(self):
        self.login()

        response = self.client.get(reverse("task_marketplace"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Active Task")
        self.assertNotContains(response, "Paused Task")

    def test_get_claim_does_not_claim_task(self):
        self.login()

        response = self.client.get(
            reverse("claim_task", args=[self.active_task.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            TaskClaim.objects.filter(
                task=self.active_task,
                worker=self.user,
            ).count(),
            0,
        )
        self.active_task.refresh_from_db()
        self.assertEqual(self.active_task.completed_workers, 0)

    def test_worker_can_claim_active_task(self):
        self.login()

        response = self.client.post(
            reverse("claim_task", args=[self.active_task.id])
        )

        self.assertRedirects(response, reverse("task_marketplace"))

        self.assertTrue(
            TaskClaim.objects.filter(
                task=self.active_task,
                worker=self.user,
                status="claimed",
            ).exists()
        )

        self.active_task.refresh_from_db()
        self.assertEqual(self.active_task.completed_workers, 1)
        self.assertEqual(self.active_task.status, "active")

    def test_worker_cannot_claim_same_task_twice(self):
        self.login()

        self.client.post(
            reverse("claim_task", args=[self.active_task.id])
        )
        self.client.post(
            reverse("claim_task", args=[self.active_task.id])
        )

        self.assertEqual(
            TaskClaim.objects.filter(
                task=self.active_task,
                worker=self.user,
            ).count(),
            1,
        )

        self.active_task.refresh_from_db()
        self.assertEqual(self.active_task.completed_workers, 1)

    def test_full_task_cannot_be_claimed(self):
        self.active_task.max_workers = 1
        self.active_task.completed_workers = 1
        self.active_task.status = "active"
        self.active_task.save(
            update_fields=["max_workers", "completed_workers", "status"]
        )

        self.login()

        response = self.client.post(
            reverse("claim_task", args=[self.active_task.id])
        )

        self.assertRedirects(response, reverse("task_marketplace"))
        self.assertFalse(
            TaskClaim.objects.filter(
                task=self.active_task,
                worker=self.user,
            ).exists()
        )

    def test_last_available_slot_completes_task(self):
        self.active_task.max_workers = 1
        self.active_task.save(update_fields=["max_workers"])

        self.login()

        response = self.client.post(
            reverse("claim_task", args=[self.active_task.id])
        )

        self.assertRedirects(response, reverse("task_marketplace"))

        self.active_task.refresh_from_db()
        self.assertEqual(self.active_task.completed_workers, 1)
        self.assertEqual(self.active_task.status, "completed")

    def test_submit_requires_existing_claim(self):
        self.login()

        response = self.client.get(
            reverse("submit_task", args=[self.active_task.id])
        )

        self.assertEqual(response.status_code, 404)

    def test_claimed_worker_can_submit_proof(self):
        claim = TaskClaim.objects.create(
            task=self.active_task,
            worker=self.user,
            status="claimed",
        )

        self.login()

        response = self.client.post(
            reverse("submit_task", args=[self.active_task.id]),
            {"proof": "Completed the task successfully."},
        )

        self.assertRedirects(response, reverse("task_marketplace"))

        claim.refresh_from_db()
        self.assertEqual(claim.status, "submitted")
        self.assertEqual(
            claim.proof,
            "Completed the task successfully.",
        )
        self.assertIsNotNone(claim.submitted_at)

    def test_submit_page_escapes_task_content(self):
        claim = TaskClaim.objects.create(
            task=self.active_task,
            worker=self.user,
            status="claimed",
        )
        self.active_task.title = "<script>alert('x')</script>"
        self.active_task.description = "<img src=x onerror=alert('x')>"
        self.active_task.save(update_fields=["title", "description"])

        self.login()

        response = self.client.get(
            reverse("submit_task", args=[self.active_task.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "&lt;script&gt;alert(&#x27;x&#x27;)&lt;/script&gt;", html=False)
        self.assertContains(response, "&lt;img src=x onerror=alert(&#x27;x&#x27;)&gt;", html=False)

    def test_empty_proof_does_not_submit(self):
        claim = TaskClaim.objects.create(
            task=self.active_task,
            worker=self.user,
            status="claimed",
        )

        self.login()

        response = self.client.post(
            reverse("submit_task", args=[self.active_task.id]),
            {"proof": "   "},
        )

        self.assertEqual(response.status_code, 200)

        claim.refresh_from_db()
        self.assertEqual(claim.status, "claimed")
        self.assertEqual(claim.proof, "")
        self.assertIsNone(claim.submitted_at)
