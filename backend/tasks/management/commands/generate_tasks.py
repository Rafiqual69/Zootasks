from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from tasks.models import Task


TASK_TEMPLATES = [
    {
        "title": "Website Visit Practice Task",
        "description": (
            "Visit the provided website and carefully review its publicly "
            "available information. Submit a short summary as proof."
        ),
        "category": "Website Review",
        "reward": Decimal("2.00"),
        "max_workers": 10,
    },
    {
        "title": "Content Quality Review Task",
        "description": (
            "Read the assigned content and report spelling, formatting, "
            "or clarity issues. Do not submit copied or false information."
        ),
        "category": "Content Review",
        "reward": Decimal("3.00"),
        "max_workers": 10,
    },
    {
        "title": "App Usability Feedback Task",
        "description": (
            "Use the assigned application or demo page and provide "
            "honest feedback about usability and visible issues."
        ),
        "category": "App Testing",
        "reward": Decimal("5.00"),
        "max_workers": 5,
    },
]


class Command(BaseCommand):
    help = "Create safe ZooTasks tasks from predefined templates."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show planned tasks without creating them.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=1,
            help="Maximum number of tasks to create.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        limit = max(1, min(options["limit"], len(TASK_TEMPLATES)))

        created_count = 0
        skipped_count = 0

        for template in TASK_TEMPLATES[:limit]:
            exists = Task.objects.filter(
                title=template["title"],
                status__in=["active", "paused"],
            ).exists()

            if exists:
                self.stdout.write(
                    self.style.WARNING(
                        f"SKIP: Already exists — {template['title']}"
                    )
                )
                skipped_count += 1
                continue

            deadline = timezone.now() + timedelta(days=7)

            if dry_run:
                self.stdout.write(
                    self.style.NOTICE(
                        f"DRY-RUN: Would create — {template['title']}"
                    )
                )
                continue

            Task.objects.create(
                title=template["title"],
                description=template["description"],
                category=template["category"],
                reward=template["reward"],
                max_workers=template["max_workers"],
                deadline=deadline,
                status="active",
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"CREATED: {template['title']} "
                    f"(Reward: ৳{template['reward']})"
                )
            )
            created_count += 1

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Completed. Created: {created_count}, "
                f"Skipped: {skipped_count}, Dry-run: {dry_run}"
            )
        )
