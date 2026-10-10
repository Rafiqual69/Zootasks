from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase

from .models import Task, TaskClaim


class TaskCapacityInvariantTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="task_invariant_worker",
            password="test-password-123",
        )

    def test_reserved_workers_cannot_exceed_max_workers(self):
        task = Task.objects.create(
            title="Invariant task",
            description="Test",
            reward="1.00",
            max_workers=1,
            reserved_workers=1,
            completed_workers=0,
        )
        self.assertEqual(task.reserved_workers, 1)
        task.reserved_workers = 2
        with self.assertRaises(IntegrityError):
            task.save(update_fields=["reserved_workers"])

    def test_completed_workers_cannot_exceed_reserved_workers(self):
        task = Task.objects.create(
            title="Invariant task",
            description="Test",
            reward="1.00",
            max_workers=2,
            reserved_workers=1,
            completed_workers=1,
        )
        task.completed_workers = 2
        with self.assertRaises(IntegrityError):
            task.save(update_fields=["completed_workers"])

    def test_rejected_claim_is_not_a_capacity_reservation(self):
        task = Task.objects.create(
            title="Invariant task",
            description="Test",
            reward="1.00",
            max_workers=2,
            reserved_workers=0,
            completed_workers=0,
        )
        TaskClaim.objects.create(
            task=task,
            worker=self.user,
            status="rejected",
        )
        self.assertEqual(
            task.claims.exclude(status="rejected").count(),
            task.reserved_workers,
        )
