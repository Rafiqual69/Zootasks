from django.contrib import admin
from django.contrib.auth.models import Group, Permission, User
from django.core.management import call_command
from django.test import RequestFactory, TestCase
from django.test import override_settings
from django.urls import reverse

from wallet.models import WalletTransaction, WithdrawalRequest

from accounts.admin import GroupAdmin, UserAdmin
from accounts.models import WorkerProfile, AccountEntity
from promotions.admin import PromotionAdmin
from promotions.models import Promotion
from tasks.admin import TaskAdmin
from tasks.models import Task


class LiveWalletDashboardPermissionTests(TestCase):
    def setUp(self):
        self.url = reverse("live_wallet_dashboard")
        self.staff = User.objects.create_user(
            username="finance_viewer",
            password="test-password-123",
            is_staff=True,
        )
        self.permission = Permission.objects.get(
            content_type__app_label="wallet",
            codename="view_live_wallet_dashboard",
        )

    def test_staff_without_dashboard_permission_is_forbidden(self):
        self.client.force_login(self.staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_staff_with_dashboard_permission_can_view_dashboard(self):
        self.staff.user_permissions.add(self.permission)
        self.client.force_login(self.staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Live Wallet Dashboard")
        self.assertContains(response, "Finance Control Center")
        self.assertContains(response, "Withdrawal control")
        self.assertContains(response, "Controlled finance lifecycle")
        self.assertContains(response, "Request")
        self.assertContains(response, "Reconcile")

    def test_superuser_can_view_dashboard_without_explicit_permission(self):
        self.staff.is_superuser = True
        self.staff.save(update_fields=["is_superuser"])
        self.client.force_login(self.staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)


class FinanceRBACSetupTests(TestCase):
    def setUp(self):
        self.pay = Permission.objects.get(
            content_type__app_label="wallet",
            codename="mark_withdrawal_paid",
        )
        self.dashboard = Permission.objects.get(
            content_type__app_label="wallet",
            codename="view_live_wallet_dashboard",
        )
        self.approve = Permission.objects.get(
            content_type__app_label="wallet",
            codename="approve_withdrawal",
        )
        self.reject = Permission.objects.get(
            content_type__app_label="wallet",
            codename="reject_withdrawal",
        )

    def test_setup_rbac_separates_finance_approval_and_payment(self):
        call_command("setup_rbac")

        finance = Group.objects.get(name="Finance")
        payer = Group.objects.get(name="Finance Payer")
        super_admin = Group.objects.get(name="Super Admin")

        self.assertTrue(finance.permissions.filter(pk=self.approve.pk).exists())
        self.assertTrue(finance.permissions.filter(pk=self.reject.pk).exists())
        self.assertTrue(finance.permissions.filter(pk=self.dashboard.pk).exists())
        self.assertFalse(finance.permissions.filter(pk=self.pay.pk).exists())

        self.assertTrue(payer.permissions.filter(pk=self.pay.pk).exists())
        self.assertTrue(payer.permissions.filter(pk=self.dashboard.pk).exists())
        self.assertFalse(payer.permissions.filter(pk=self.approve.pk).exists())
        self.assertFalse(payer.permissions.filter(pk=self.reject.pk).exists())

        self.assertTrue(
            super_admin.permissions.filter(pk=self.dashboard.pk).exists()
        )


class PrivilegedFinanceSecurityAuditTests(TestCase):
    def test_security_audit_passes_after_rbac_setup(self):
        owner_user = User.objects.create_superuser(
            username="security_audit_owner",
            password="test-password-123",
        )
        AccountEntity.objects.create(
            user=owner_user,
            entity_type=AccountEntity.EntityType.OWNER,
            is_active=True,
        )

        call_command("setup_rbac")
        call_command("audit_security")

    def test_wallet_financial_records_are_not_directly_editable_in_admin(self):
        request = RequestFactory().get("/admin/")
        request.user = User.objects.create_superuser(
            username="audit_admin",
            password="test-password-123",
        )

        wallet_admin = admin.site._registry[WalletTransaction]
        withdrawal_admin = admin.site._registry[WithdrawalRequest]

        for model_admin in (wallet_admin, withdrawal_admin):
            self.assertFalse(model_admin.has_add_permission(request))
            self.assertFalse(model_admin.has_change_permission(request))
            self.assertFalse(model_admin.has_delete_permission(request))


class WorkerProfileAdminProtectionTests(TestCase):
    def test_worker_profile_financial_state_is_read_only_and_not_deletable(self):
        request = RequestFactory().get("/admin/")
        request.user = User.objects.create_superuser(
            username="profile_admin",
            password="test-password-123",
        )

        from accounts.admin import WorkerProfileAdmin

        model_admin = WorkerProfileAdmin(WorkerProfile, admin.site)

        self.assertFalse(model_admin.has_add_permission(request))
        self.assertFalse(model_admin.has_delete_permission(request))

        for field_name in (
            "user",
            "balance",
            "reserved_balance",
            "total_earned",
            "completed_tasks",
            "created_at",
        ):
            self.assertIn(field_name, model_admin.readonly_fields)


class RootObjectAdminProtectionTests(TestCase):
    def setUp(self):
        self.owner_request = RequestFactory().get("/admin/")
        self.owner_request.user = User.objects.create_superuser(
            username="root_object_owner",
            password="test-password-123",
        )
        AccountEntity.objects.create(
            user=self.owner_request.user,
            entity_type=AccountEntity.EntityType.OWNER,
            is_active=True,
        )
        self.staff_request = RequestFactory().get("/admin/")
        self.staff_request.user = User.objects.create_user(
            username="root_object_staff",
            password="test-password-123",
            is_staff=True,
        )

    @override_settings(OWNER_USERNAME="root_object_owner")
    def test_task_admin_creation_is_owner_controlled(self):
        model_admin = TaskAdmin(Task, admin.site)

        self.assertTrue(model_admin.has_add_permission(self.owner_request))
        non_owner = RequestFactory().get("/admin/")
        non_owner.user = User.objects.create_superuser(username="root_object_other_superuser", password="test-password-123")
        self.assertFalse(model_admin.has_add_permission(non_owner))
        self.assertFalse(model_admin.has_add_permission(self.staff_request))
        self.assertFalse(model_admin.has_delete_permission(self.owner_request))

    @override_settings(OWNER_USERNAME="root_object_owner")
    def test_task_add_form_keeps_initial_financial_fields_editable(self):
        model_admin = TaskAdmin(Task, admin.site)

        readonly = model_admin.get_readonly_fields(self.owner_request)

        self.assertNotIn("reward", readonly)
        self.assertNotIn("max_workers", readonly)
        self.assertIn("completed_workers", readonly)
        self.assertIn("created_at", readonly)

    @override_settings(OWNER_USERNAME="root_object_owner")
    def test_existing_task_financial_and_lifecycle_fields_are_read_only(self):
        model_admin = TaskAdmin(Task, admin.site)
        existing = Task(id=1)

        readonly = model_admin.get_readonly_fields(
            self.owner_request,
            existing,
        )

        for field_name in (
            "reward",
            "max_workers",
            "completed_workers",
            "status",
            "created_at",
        ):
            self.assertIn(field_name, readonly)

    @override_settings(OWNER_USERNAME="root_object_owner")
    def test_promotion_admin_creation_is_owner_controlled(self):
        model_admin = PromotionAdmin(Promotion, admin.site)

        self.assertTrue(model_admin.has_add_permission(self.owner_request))
        non_owner = RequestFactory().get("/admin/")
        non_owner.user = User.objects.create_superuser(username="promotion_other_superuser", password="test-password-123")
        self.assertFalse(model_admin.has_add_permission(non_owner))
        self.assertFalse(model_admin.has_add_permission(self.staff_request))
        self.assertFalse(model_admin.has_delete_permission(self.owner_request))

    @override_settings(OWNER_USERNAME="root_object_owner")
    def test_promotion_add_form_keeps_initial_financial_fields_editable(self):
        model_admin = PromotionAdmin(Promotion, admin.site)

        readonly = model_admin.get_readonly_fields(self.owner_request)

        self.assertNotIn("reward", readonly)
        self.assertNotIn("budget", readonly)
        self.assertNotIn("max_workers", readonly)
        self.assertIn("completed_workers", readonly)
        self.assertIn("status", readonly)
        self.assertIn("created_at", readonly)

    @override_settings(OWNER_USERNAME="root_object_owner")
    def test_existing_promotion_financial_and_lifecycle_fields_are_read_only(self):
        model_admin = PromotionAdmin(Promotion, admin.site)
        existing = Promotion(id=1)

        for field_name in (
            "reward",
            "budget",
            "max_workers",
            "completed_workers",
            "status",
            "created_at",
        ):
            self.assertIn(
                field_name,
                model_admin.get_readonly_fields(
                    self.owner_request,
                    existing,
                ),
            )


class UserAdminPrivilegeProtectionTests(TestCase):
    def setUp(self):
        self.request = RequestFactory().get("/admin/")
        self.request.user = User.objects.create_superuser(
            username="user_admin_audit",
            password="test-password-123",
        )

    def test_user_creation_and_deletion_are_disabled(self):
        model_admin = UserAdmin(User, admin.site)

        self.assertFalse(model_admin.has_add_permission(self.request))
        self.assertFalse(model_admin.has_delete_permission(self.request))

    def test_user_privilege_fields_are_read_only(self):
        model_admin = UserAdmin(User, admin.site)

        for field_name in (
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
            "last_login",
            "date_joined",
        ):
            self.assertIn(field_name, model_admin.readonly_fields)


class GroupAdminPrivilegeProtectionTests(TestCase):
    def setUp(self):
        self.request = RequestFactory().get("/admin/")
        self.request.user = User.objects.create_superuser(
            username="group_admin_audit",
            password="test-password-123",
        )

    def test_group_creation_change_and_deletion_are_disabled(self):
        model_admin = GroupAdmin(Group, admin.site)

        self.assertFalse(model_admin.has_add_permission(self.request))
        self.assertFalse(model_admin.has_change_permission(self.request))
        self.assertFalse(model_admin.has_delete_permission(self.request))
