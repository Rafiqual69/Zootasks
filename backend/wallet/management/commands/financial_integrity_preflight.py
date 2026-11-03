from django.core.management.base import BaseCommand, CommandError
from django.db.models import F, Q

from accounts.models import WorkerProfile
from promotions.models import Promotion
from tasks.models import Task
from wallet.models import WalletTransaction, WithdrawalRequest


class Command(BaseCommand):
    help = (
        "Read-only financial integrity preflight. Reports suspicious existing "
        "rows without changing wallet balances, transactions, claims, or requests."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--fail-on-findings",
            action="store_true",
            help="Exit with an error if any integrity finding is detected.",
        )

    def handle(self, *args, **options):
        checks = (
            ("tasks.non_positive_reward", Task.objects.filter(reward__lte=0)),
            (
                "tasks.completed_workers_exceed_max",
                Task.objects.filter(completed_workers__gt=F("max_workers")),
            ),
            ("promotions.negative_reward", Promotion.objects.filter(reward__lt=0)),
            ("promotions.negative_budget", Promotion.objects.filter(budget__lt=0)),
            (
                "promotions.completed_workers_exceed_max",
                Promotion.objects.filter(completed_workers__gt=F("max_workers")),
            ),
            (
                "wallet.earning_non_positive",
                WalletTransaction.objects.filter(
                    transaction_type="earning",
                    amount__lte=0,
                ),
            ),
            (
                "wallet.withdrawal_non_positive",
                WalletTransaction.objects.filter(
                    transaction_type="withdrawal",
                    amount__lte=0,
                ),
            ),
            (
                "withdrawals.non_positive_amount",
                WithdrawalRequest.objects.filter(amount__lte=0),
            ),
            (
                "profiles.negative_financial_value",
                WorkerProfile.objects.filter(
                    Q(balance__lt=0)
                    | Q(reserved_balance__lt=0)
                    | Q(total_earned__lt=0)
                ),
            ),
            (
                "profiles.reserved_exceeds_balance",
                WorkerProfile.objects.filter(
                    reserved_balance__gt=F("balance")
                ),
            ),
        )

        total_findings = 0
        self.stdout.write("ZooTasks financial integrity preflight (READ ONLY)")
        for check_name, queryset in checks:
            count = queryset.count()
            total_findings += count
            self.stdout.write(f"{check_name}: {count}")

        self.stdout.write(f"Total finding counts: {total_findings}")
        self.stdout.write("No records were modified.")

        if total_findings:
            self.stdout.write(
                self.style.WARNING(
                    "Review findings before adding database constraints or migrating."
                )
            )
            if options["fail_on_findings"]:
                raise CommandError(
                    "Financial integrity findings detected; no data was changed."
                )
        else:
            self.stdout.write(
                self.style.SUCCESS("No financial integrity findings detected.")
            )
