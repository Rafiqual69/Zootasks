from types import SimpleNamespace

from django.conf import settings

from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError

from accounts.admin import GroupAdmin, UserAdmin
from accounts.models import WorkerProfile
from promotions.admin import PromotionAdmin
from promotions.models import Promotion
from tasks.admin import TaskAdmin
from tasks.models import Task
from wallet.admin import WalletTransactionAdmin, WithdrawalRequestAdmin
from wallet.models import WalletTransaction, WithdrawalRequest


class Command(BaseCommand):
    help = "Run automated security/RBAC invariants for privileged finance controls."

    def handle(self, *args, **options):
        required = [
            ("approve_withdrawal", "wallet"),
            ("reject_withdrawal", "wallet"),
            ("mark_withdrawal_paid", "wallet"),
            ("view_live_wallet_dashboard", "wallet"),
        ]

        permissions = {}
        for codename, app_label in required:
            try:
                permissions[codename] = Permission.objects.get(
                    content_type__app_label=app_label,
                    codename=codename,
                )
            except Permission.DoesNotExist as exc:
                raise CommandError(
                    f"Missing required permission: {app_label}.{codename}"
                ) from exc

        try:
            finance = Group.objects.get(name="Finance")
            payer = Group.objects.get(name="Finance Payer")
        except Group.DoesNotExist as exc:
            raise CommandError(
                "Required finance RBAC groups are missing. Run setup_rbac first."
            ) from exc

        def has(group, codename):
            return group.permissions.filter(
                pk=permissions[codename].pk
            ).exists()

        owner_request = SimpleNamespace(
            user=SimpleNamespace(
                is_superuser=True,
                get_username=lambda: settings.OWNER_USERNAME,
            )
        )
        non_owner_superuser_request = SimpleNamespace(
            user=SimpleNamespace(
                is_superuser=True,
                get_username=lambda: "not-the-owner",
            )
        )
        staff_request = SimpleNamespace(
            user=SimpleNamespace(is_superuser=False)
        )

        task_admin = TaskAdmin(Task, admin.site)
        promotion_admin = PromotionAdmin(Promotion, admin.site)

        existing_task = Task(id=1)
        existing_promotion = Promotion(id=1)

        checks = {
            "Finance can approve": has(finance, "approve_withdrawal"),
            "Finance can reject": has(finance, "reject_withdrawal"),
            "Finance can view dashboard": has(finance, "view_live_wallet_dashboard"),
            "Finance cannot pay": not has(finance, "mark_withdrawal_paid"),
            "Finance Payer can pay": has(payer, "mark_withdrawal_paid"),
            "Finance Payer can view dashboard": has(
                payer, "view_live_wallet_dashboard"
            ),
            "Finance Payer cannot approve": not has(payer, "approve_withdrawal"),
            "Finance Payer cannot reject": not has(payer, "reject_withdrawal"),
            "Wallet ledger admin is immutable": all(
                not getattr(WalletTransactionAdmin, method, lambda *a: True)(
                    WalletTransactionAdmin(WalletTransaction, admin.site),
                    owner_request,
                )
                for method in (
                    "has_add_permission",
                    "has_change_permission",
                    "has_delete_permission",
                )
            ),
            "User admin cannot add": not UserAdmin.has_add_permission(
                UserAdmin.__new__(UserAdmin), owner_request
            ),
            "User admin cannot delete": not UserAdmin.has_delete_permission(
                UserAdmin.__new__(UserAdmin), owner_request
            ),
            "User privilege fields are read-only": all(
                field in UserAdmin.readonly_fields
                for field in (
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            ),
            "Group admin cannot add": not GroupAdmin.has_add_permission(
                GroupAdmin.__new__(GroupAdmin), owner_request
            ),
            "Group admin cannot change": not GroupAdmin.has_change_permission(
                GroupAdmin.__new__(GroupAdmin), owner_request
            ),
            "Group admin cannot delete": not GroupAdmin.has_delete_permission(
                GroupAdmin.__new__(GroupAdmin), owner_request
            ),
            "Withdrawal records are action-controlled": all(
                not getattr(WithdrawalRequestAdmin, method, lambda *a: True)(
                    WithdrawalRequestAdmin(WithdrawalRequest, admin.site),
                    owner_request,
                )
                for method in (
                    "has_add_permission",
                    "has_change_permission",
                    "has_delete_permission",
                )
            ),
            "Task creation is Owner-controlled": (
                task_admin.has_add_permission(owner_request)
                and not task_admin.has_add_permission(non_owner_superuser_request)
                and not task_admin.has_add_permission(staff_request)
                and not task_admin.has_delete_permission(owner_request)
            ),
            "Task existing financial fields are read-only": all(
                field in task_admin.get_readonly_fields(
                    owner_request,
                    existing_task,
                )
                for field in (
                    "reward",
                    "max_workers",
                    "completed_workers",
                    "status",
                    "created_at",
                )
            ),
            "Promotion creation is Owner-controlled": (
                promotion_admin.has_add_permission(owner_request)
                and not promotion_admin.has_add_permission(non_owner_superuser_request)
                and not promotion_admin.has_add_permission(staff_request)
                and not promotion_admin.has_delete_permission(owner_request)
            ),
            "Promotion existing financial fields are read-only": all(
                field in promotion_admin.get_readonly_fields(
                    owner_request,
                    existing_promotion,
                )
                for field in (
                    "reward",
                    "budget",
                    "max_workers",
                    "completed_workers",
                    "status",
                    "created_at",
                )
            ),
        }

        _ = (
            UserAdmin,
            GroupAdmin,
            WorkerProfile,
            Task,
            Promotion,
            WalletTransaction,
            WithdrawalRequest,
        )

        failed = [name for name, passed in checks.items() if not passed]

        for name, passed in checks.items():
            mark = "PASS" if passed else "FAIL"
            style = self.style.SUCCESS if passed else self.style.ERROR
            self.stdout.write(style(f"[{mark}] {name}"))

        if failed:
            raise CommandError(
                "Security audit failed: " + "; ".join(failed)
            )

        self.stdout.write(
            self.style.SUCCESS(
                "ZooTasks privileged finance security audit passed."
            )
        )
