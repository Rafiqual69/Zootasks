from django.core.management.base import BaseCommand
from django.db import models
from django.utils import timezone

from core.security_policy_engine import require_authorized

from tasks.models import Task


class Command(BaseCommand):
    help = "Expire overdue ZooTasks and close tasks that reached worker capacity."

    def handle(self, *args, **options):
        now = timezone.now()

        require_authorized(
            actor="system",
            resource="task",
            action="update",
            scope="automation",
            facts={
                "trusted_execution_context": True,
                "automation.task_lifecycle_bounded": True,
                "automation.no_external_side_effect": True,
            },
        )

        expired_count = Task.objects.filter(
            status__in=["active", "paused"],
            deadline__isnull=False,
            deadline__lt=now,
        ).update(status="expired")

        completed_count = Task.objects.filter(
            status__in=["active", "paused"],
            max_workers__gt=0,
            completed_workers__gte=models.F("max_workers"),
        ).update(status="completed")

        self.stdout.write(
            self.style.SUCCESS(
                f"Task maintenance complete. "
                f"Expired: {expired_count}, "
                f"Completed: {completed_count}"
            )
        )
