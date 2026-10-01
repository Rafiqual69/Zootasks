from django.contrib import admin
from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse
from decimal import Decimal

from .admin import TaskAdmin, approve_submissions, reject_submissions
from .models import Task, TaskClaim
from .services import (
    TaskServiceError,
    approve_claim,
    claim_task_for_worker,
    reject_claim,
    submit_claim_proof,
)
from accounts.models import WorkerProfile
from wallet.models import WalletTransaction


class TaskAdminAuditProtectionTests(TestCase):
    def test_task_and_claim_deletion_is_disabled(self):
        task_admin = TaskAdmin(Task, admin.site)
        from .admin import TaskClaimAdmin
        claim_admin = TaskClaimAdmin(TaskClaim, admin.site)

        self.assertFalse(task_admin.has_delete_permission(None))
        self.assertFalse(claim_admin.has_delete_permission(None))


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
        self.assertEqual(self.active_task.claimed_workers, 0)
        self.assertEqual(self.active_task.completed_workers, 0)

    def test_worker_can_claim_active_task_without_marking_completion(self):
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
        self.assertEqual(self.active_task.claimed_workers, 1)
        self.assertEqual(self.active_task.completed_workers, 0)
        self.assertEqual(self.active_task.status, "active")

    def test_worker_cannot_claim_same_task_twice(self):
        self.login()

        self.client.post(reverse("claim_task", args=[self.active_task.id]))
        self.client.post(reverse("claim_task", args=[self.active_task.id]))

        self.assertEqual(
            TaskClaim.objects.filter(
                task=self.active_task,
                worker=self.user,
            ).count(),
            1,
        )

        self.active_task.refresh_from_db()
        self.assertEqual(self.active_task.claimed_workers, 1)
        self.assertEqual(self.active_task.completed_workers, 0)

    def test_rejected_claim_can_reclaim_an_available_slot(self):
        claim = TaskClaim.objects.create(
            task=self.active_task,
            worker=self.user,
            status="rejected",
        )

        self.login()

        response = self.client.post(
            reverse("claim_task", args=[self.active_task.id])
        )

        self.assertRedirects(response, reverse("task_marketplace"))

        claim.refresh_from_db()
        self.active_task.refresh_from_db()
        self.assertEqual(claim.status, "claimed")
        self.assertEqual(self.active_task.claimed_workers, 1)

    def test_full_task_cannot_be_claimed(self):
        self.active_task.max_workers = 1
        self.active_task.claimed_workers = 1
        self.active_task.save(update_fields=["max_workers", "claimed_workers"])

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

    def test_last_available_slot_stays_active_until_work_is_approved(self):
        self.active_task.max_workers = 1
        self.active_task.save(update_fields=["max_workers"])

        self.login()

        self.client.post(reverse("claim_task", args=[self.active_task.id]))

        self.active_task.refresh_from_db()
        self.assertEqual(self.active_task.claimed_workers, 1)
        self.assertEqual(self.active_task.completed_workers, 0)
        self.assertEqual(self.active_task.status, "active")

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
        self.active_task.claimed_workers = 1
        self.active_task.save(update_fields=["claimed_workers"])

        self.login()

        response = self.client.post(
            reverse("submit_task", args=[self.active_task.id]),
            {"proof": "Completed the task successfully."},
        )

        self.assertRedirects(response, reverse("task_marketplace"))

        claim.refresh_from_db()
        self.assertEqual(claim.status, "submitted")
        self.assertEqual(claim.proof, "Completed the task successfully.")
        self.assertIsNotNone(claim.submitted_at)

    def test_submit_page_escapes_task_content(self):
        claim = TaskClaim.objects.create(
            task=self.active_task,
            worker=self.user,
            status="claimed",
        )
        self.active_task.claimed_workers = 1
        self.active_task.save(update_fields=["claimed_workers"])
        self.active_task.title = "<script>alert('x')</script>"
        self.active_task.description = "<img src=x onerror=alert('x')>"
        self.active_task.save(update_fields=["title", "description"])

        self.login()

        response = self.client.get(
            reverse("submit_task", args=[self.active_task.id])
        )

        self.assertEqual(response.status_code, 200)

    def test_empty_proof_does_not_submit(self):
        claim = TaskClaim.objects.create(
            task=self.active_task,
            worker=self.user,
            status="claimed",
        )
        self.active_task.claimed_workers = 1
        self.active_task.save(update_fields=["claimed_workers"])

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


class TaskSubmissionLifecycleTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="task_reviewer",
            password="StrongTestPass123!",
        )
        self.worker = User.objects.create_user(
            username="task_worker",
            password="StrongTestPass123!",
        )
        self.task = Task.objects.create(
            title="Reviewable Task",
            description="Review this task.",
            reward="25.00",
            max_workers=1,
        )
        self.claim = TaskClaim.objects.create(
            task=self.task,
            worker=self.worker,
            status="submitted",
            proof="proof",
        )
        self.task.claimed_workers = 1
        self.task.save(update_fields=["claimed_workers"])

    def test_approval_moves_worker_from_claimed_to_completed(self):
        permission = Permission.objects.get(
            content_type__app_label="tasks",
            codename="approve_task_submission",
        )
        self.owner.user_permissions.add(permission)
        request = type("Request", (), {"user": self.owner})()

        messages = []
        modeladmin = type(
            "ModelAdmin",
            (),
            {"message_user": lambda self, request, message, level=None: messages.append(message)},
        )()

        approve_submissions(modeladmin, request, TaskClaim.objects.filter(pk=self.claim.pk))

        self.claim.refresh_from_db()
        self.task.refresh_from_db()
        self.assertEqual(self.claim.status, "approved")
        self.assertEqual(self.task.claimed_workers, 1)
        self.assertEqual(self.task.completed_workers, 1)
        self.assertEqual(self.task.status, "completed")
        self.assertTrue(WalletTransaction.objects.filter(task_claim=self.claim).exists())

    def test_rejection_releases_claimed_slot(self):
        permission = Permission.objects.get(
            content_type__app_label="tasks",
            codename="reject_task_submission",
        )
        self.owner.user_permissions.add(permission)
        request = type("Request", (), {"user": self.owner})()

        messages = []
        modeladmin = type(
            "ModelAdmin",
            (),
            {"message_user": lambda self, request, message, level=None: messages.append(message)},
        )()

        reject_submissions(modeladmin, request, TaskClaim.objects.filter(pk=self.claim.pk))

        self.claim.refresh_from_db()
        self.task.refresh_from_db()
        self.assertEqual(self.claim.status, "rejected")
        self.assertEqual(self.task.claimed_workers, 0)
        self.assertEqual(self.task.completed_workers, 0)
        self.assertEqual(self.task.status, "active")


class TaskServiceLifecycleTests(TestCase):
    def setUp(self):
        self.worker = User.objects.create_user(
            username="service_worker",
            password="StrongTestPass123!",
        )
        self.task = Task.objects.create(
            title="Service Task",
            description="Use the shared task service.",
            reward="30.00",
            max_workers=1,
        )

    def test_claim_service_reserves_capacity_not_completion(self):
        claim = claim_task_for_worker(
            user=self.worker,
            task_id=self.task.id,
        )

        self.assertEqual(claim.status, "claimed")
        self.task.refresh_from_db()
        self.assertEqual(self.task.claimed_workers, 1)
        self.assertEqual(self.task.completed_workers, 0)
        self.assertEqual(self.task.status, "active")

    def test_submit_service_changes_only_claim_state(self):
        claim = claim_task_for_worker(
            user=self.worker,
            task_id=self.task.id,
        )

        submitted = submit_claim_proof(
            user=self.worker,
            task_id=self.task.id,
            proof="valid proof",
        )

        self.assertEqual(submitted.id, claim.id)
        self.assertEqual(submitted.status, "submitted")
        self.task.refresh_from_db()
        self.assertEqual(self.task.completed_workers, 0)

    def test_reject_service_releases_capacity(self):
        claim = claim_task_for_worker(
            user=self.worker,
            task_id=self.task.id,
        )
        submit_claim_proof(
            user=self.worker,
            task_id=self.task.id,
            proof="valid proof",
        )

        _, result = reject_claim(claim_id=claim.id)

        self.assertEqual(result, "rejected")
        self.task.refresh_from_db()
        self.assertEqual(self.task.claimed_workers, 0)
        self.assertEqual(self.task.completed_workers, 0)

    def test_approve_service_pays_once_and_marks_completion(self):
        claim = claim_task_for_worker(
            user=self.worker,
            task_id=self.task.id,
        )
        submit_claim_proof(
            user=self.worker,
            task_id=self.task.id,
            proof="valid proof",
        )

        _, result = approve_claim(claim_id=claim.id)

        self.assertEqual(result, "approved")
        self.task.refresh_from_db()
        self.assertEqual(self.task.claimed_workers, 1)
        self.assertEqual(self.task.completed_workers, 1)
        self.assertEqual(self.task.status, "completed")
        self.assertEqual(
            WalletTransaction.objects.filter(task_claim=claim).count(),
            1,
        )

        profile = WorkerProfile.objects.get(user=self.worker)
        self.assertEqual(profile.balance, Decimal("30.00"))
        self.assertEqual(profile.total_earned, Decimal("30.00"))
        self.assertEqual(profile.completed_tasks, 1)
