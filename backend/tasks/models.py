from django.contrib.auth.models import User
from django.db import models


class Task(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("paused", "Paused"),
        ("completed", "Completed"),
        ("expired", "Expired"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100, default="General")
    reward = models.DecimalField(max_digits=10, decimal_places=2)
    max_workers = models.PositiveIntegerField(default=1)
    completed_workers = models.PositiveIntegerField(default=0)
    deadline = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        permissions = [
            ("approve_task_submission", "Can approve task submissions"),
            ("reject_task_submission", "Can reject task submissions"),
        ]

    def __str__(self):
        return self.title


class TaskClaim(models.Model):
    STATUS_CHOICES = [
        ("claimed", "Claimed"),
        ("submitted", "Submitted"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="claims",
    )
    worker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="task_claims",
    )
    proof = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="claimed",
    )
    claimed_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["task", "worker"],
                name="unique_task_worker",
            )
        ]

    def __str__(self):
        return f"{self.worker.username} - {self.task.title}"
