from decimal import Decimal
from unittest.mock import patch

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import AccountEntity, WorkerProfile
from wallet.models import WalletTransaction
from .admin import approve_submissions, reject_submissions
from .models import Task, TaskClaim


class TaskClaimWorkflowReconciliationTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="task_workflow_worker",
            password="test-password-123",
        )
        AccountEntity.objects.create(
            user=self.user,
            entity_type=AccountEntity.EntityType.WORKER,
        )
        WorkerProfile.objects.create(
            user=self.user,
            balance=Decimal("100.00"),
            reserved_balance=Decimal("0.00"),
            total_earned=Decimal("100.00"),
        )
        self.admin_user = User.objects.create_superuser(
            username="task_workflow_admin",
            password="test-admin-password",
        )
        self.task = Task.objects.create(
            title="Workflow Task",
            description="Test",
            reward=Decimal("25.00"),
            max_workers=1,
            reserved_workers=1,
            completed_workers=0,
            status="completed",
        )
        self.claim = TaskClaim.objects.create(
            task=self.task,
            worker=self.user,
            status="submitted",
        )

    def request(self):
        request = type("RequestStub", (), {})()
        request.user = self.admin_user
        return request

    def test_new_approval_increments_completed_once_and_pays(self):
        with patch("tasks.admin.require_execution_authorized"):
            approve_submissions(
                type("ModelAdminStub", (), {"message_user": lambda *args, **kwargs: None})(),
                self.request(),
                TaskClaim.objects.filter(pk=self.claim.pk),
            )

        self.claim.refresh_from_db()
        self.task.refresh_from_db()
        profile = WorkerProfile.objects.get(user=self.user)

        self.assertEqual(self.claim.status, "approved")
        self.assertEqual(self.task.completed_workers, 1)
        self.assertEqual(self.task.reserved_workers, 1)
        self.assertEqual(profile.balance, Decimal("125.00"))
        self.assertEqual(profile.total_earned, Decimal("125.00"))
        self.assertEqual(profile.completed_tasks, 1)
        self.assertEqual(
            WalletTransaction.objects.filter(
                task_claim=self.claim,
                transaction_type="earning",
            ).count(),
            1,
        )

    def test_existing_ledger_reconciliation_increments_completed_without_double_payment(self):
        WalletTransaction.objects.create(
            user=self.user,
            amount=Decimal("25.00"),
            transaction_type="earning",
            description="Existing task reward",
            task_claim=self.claim,
        )

        with patch("tasks.admin.require_execution_authorized"):
            approve_submissions(
                type("ModelAdminStub", (), {"message_user": lambda *args, **kwargs: None})(),
                self.request(),
                TaskClaim.objects.filter(pk=self.claim.pk),
            )

        self.claim.refresh_from_db()
        self.task.refresh_from_db()
        profile = WorkerProfile.objects.get(user=self.user)

        self.assertEqual(self.claim.status, "approved")
        self.assertEqual(self.task.completed_workers, 1)
        self.assertEqual(
            WalletTransaction.objects.filter(
                task_claim=self.claim,
                transaction_type="earning",
            ).count(),
            1,
        )
        self.assertEqual(profile.balance, Decimal("100.00"))
        self.assertEqual(profile.completed_tasks, 0)

    def test_rejection_releases_reservation_and_reopens_completed_task(self):
        with patch("tasks.admin.require_execution_authorized"):
            reject_submissions(
                type("ModelAdminStub", (), {"message_user": lambda *args, **kwargs: None})(),
                self.request(),
                TaskClaim.objects.filter(pk=self.claim.pk),
            )

        self.claim.refresh_from_db()
        self.task.refresh_from_db()

        self.assertEqual(self.claim.status, "rejected")
        self.assertEqual(self.task.reserved_workers, 0)
        self.assertEqual(self.task.completed_workers, 0)
        self.assertEqual(self.task.status, "active")

    def test_approved_replay_does_not_double_count_or_pay(self):
        with patch("tasks.admin.require_execution_authorized"):
            approve_submissions(
                type("ModelAdminStub", (), {"message_user": lambda *args, **kwargs: None})(),
                self.request(),
                TaskClaim.objects.filter(pk=self.claim.pk),
            )

        balance_after_first = WorkerProfile.objects.get(user=self.user).balance

        with patch("tasks.admin.require_execution_authorized"):
            approve_submissions(
                type("ModelAdminStub", (), {"message_user": lambda *args, **kwargs: None})(),
                self.request(),
                TaskClaim.objects.filter(pk=self.claim.pk),
            )

        self.task.refresh_from_db()

        self.assertEqual(self.task.completed_workers, 1)
        self.assertEqual(
            WalletTransaction.objects.filter(
                task_claim=self.claim,
                transaction_type="earning",
            ).count(),
            1,
        )
        self.assertEqual(
            WorkerProfile.objects.get(user=self.user).balance,
            balance_after_first,
        )
