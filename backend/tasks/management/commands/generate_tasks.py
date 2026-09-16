from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from tasks.models import Task


TASK_TEMPLATES = [
    {
        "title": "Website Visit Practice Task",
        "description": (
            "Visit the assigned website and review its publicly available "
            "information. Submit a short, honest summary as proof."
        ),
        "category": "Website Review",
        "reward": Decimal("2.00"),
        "max_workers": 10,
    },
    {
        "title": "Content Quality Review Task",
        "description": (
            "Review the assigned content and report spelling, formatting, "
            "or clarity issues. Submit honest feedback."
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
    {
        "title": "Public Information Research Task",
        "description": (
            "Research publicly available information on the assigned topic "
            "and submit a short factual summary with the source link."
        ),
        "category": "Research",
        "reward": Decimal("4.00"),
        "max_workers": 10,
    },
    {
        "title": "Website Usability Feedback Task",
        "description": (
            "Visit the assigned website and provide honest feedback about "
            "navigation, readability, and visible usability issues."
        ),
        "category": "Website Feedback",
        "reward": Decimal("4.00"),
        "max_workers": 10,
    },
    {
        "title": "Content Proofreading Task",
        "description": (
            "Review the assigned text for spelling, grammar, formatting, "
            "and clarity issues. Submit honest corrections."
        ),
        "category": "Proofreading",
        "reward": Decimal("3.00"),
        "max_workers": 10,
    },
]


class Command(BaseCommand):
    help = "Create safe ZooTasks tasks using rotating templates."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show the next task without creating it.",
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

        for template in TASK_TEMPLATES:
            if created_count >= limit:
                break

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
                created_count += 1
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
                f"Skipped: {skipped_count}, "
                f"Dry-run: {dry_run}"
            )
        )
