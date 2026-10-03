from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = "Configure the professional finance RBAC roles for ZooTasks."

    def handle(self, *args, **options):
        def perm(codename):
            return Permission.objects.get(
                content_type__app_label="wallet",
                codename=codename,
            )

        approve = perm("approve_withdrawal")
        reject = perm("reject_withdrawal")
        pay = perm("mark_withdrawal_paid")
        view_tx = perm("view_wallettransaction")
        view_withdrawal = perm("view_withdrawalrequest")
        view_dashboard = perm("view_live_wallet_dashboard")

        finance = Group.objects.get_or_create(name="Finance")[0]
        finance.permissions.add(
            approve,
            reject,
            view_tx,
            view_withdrawal,
            view_dashboard,
        )
        finance.permissions.remove(pay)

        finance_payer = Group.objects.get_or_create(name="Finance Payer")[0]
        finance_payer.permissions.set(
            [
                pay,
                view_tx,
                view_withdrawal,
                view_dashboard,
            ]
        )

        super_admin = Group.objects.get_or_create(name="Super Admin")[0]
        super_admin.permissions.add(view_dashboard)

        self.stdout.write(
            self.style.SUCCESS(
                "Finance RBAC configured: Finance cannot mark payments paid; "
                "Finance Payer can execute approved payments; "
                "Finance and Super Admin can view the live wallet dashboard."
            )
        )
