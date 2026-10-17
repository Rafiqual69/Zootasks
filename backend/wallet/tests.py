from decimal import Decimal

from django.contrib import admin
from django.contrib.auth.models import Permission, User
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from accounts.models import AccountEntity, WorkerProfile
from wallet.models import WalletTransaction, WithdrawalRequest
from tasks.models import Task, TaskClaim
from promotions.models import Promotion, PromotionClaim
from wallet.admin import approve_withdrawals, reject_withdrawals, mark_withdrawals_paid



class WalletTransactionAdminReadBoundaryTests(TestCase):
    def setUp(self):
        from django.test import RequestFactory
        from wallet.admin import WalletTransactionAdmin

        self.factory = RequestFactory()
        self.model_admin = WalletTransactionAdmin(
            WalletTransaction,
            admin.site,
        )
        self.worker = User.objects.create_user(
            username="ledger_worker",
            password="test-password-123",
        )
        self.tx = WalletTransaction.objects.create(
            user=self.worker,
            amount=Decimal("25.00"),
            transaction_type="earning",
            description="Test ledger entry",
        )

    def request_for(self, user):
        request = self.factory.get("/admin/wallet/wallettransaction/")
        request.user = user
        return request

    def test_unprivileged_staff_cannot_view_wallet_ledger(self):
        staff = User.objects.create_user(
            username="limited_ledger_staff",
            password="test-password-123",
            is_staff=True,
        )
        self.assertFalse(
            self.model_admin.has_view_permission(
                self.request_for(staff),
                self.tx,
            )
        )

    def test_finance_can_view_wallet_ledger(self):
        finance = User.objects.create_user(
            username="ledger_finance",
            password="test-password-123",
            is_staff=True,
        )
        finance.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="wallet",
                codename="approve_withdrawal",
            )
        )
        self.assertTrue(
            self.model_admin.has_view_permission(
                self.request_for(finance),
                self.tx,
            )
        )

    def test_payer_can_view_wallet_ledger(self):
        payer = User.objects.create_user(
            username="ledger_payer",
            password="test-password-123",
            is_staff=True,
        )
        payer.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="wallet",
                codename="mark_withdrawal_paid",
            )
        )
        self.assertTrue(
            self.model_admin.has_view_permission(
                self.request_for(payer),
                self.tx,
            )
        )

class WithdrawalFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="worker_test",
            password="test-password-123",
        )
        AccountEntity.objects.create(
            user=self.user,
            entity_type=AccountEntity.EntityType.WORKER,
        )
        self.profile = WorkerProfile.objects.create(
            user=self.user,
            balance=Decimal("200.00"),
            reserved_balance=Decimal("0.00"),
            total_earned=Decimal("200.00"),
        )
        self.client.login(
            username="worker_test",
            password="test-password-123",
        )

    def withdrawal_data(self, amount="50.00"):
        return {
            "amount": amount,
            "bank_name": "Test Bank",
            "account_holder": "Test Worker",
            "bank_account": "1234567890",
        }

    def test_non_worker_is_denied_wallet_access(self):
        owner = User.objects.create_user(
            username="wallet-owner",
            password="test-password-123",
        )
        AccountEntity.objects.create(
            user=owner,
            entity_type=AccountEntity.EntityType.OWNER,
        )
        self.client.force_login(owner)

        response = self.client.get(reverse("wallet"))

        self.assertEqual(response.status_code, 403)

    def test_valid_withdrawal_reserves_balance(self):
        response = self.client.post(
            reverse("request_withdrawal"),
            self.withdrawal_data("50.00"),
        )

        self.assertRedirects(response, reverse("withdrawal_success"))

        self.profile.refresh_from_db()
        withdrawal = WithdrawalRequest.objects.get(user=self.user)

        self.assertEqual(self.profile.balance, Decimal("200.00"))
        self.assertEqual(self.profile.reserved_balance, Decimal("50.00"))
        self.assertEqual(withdrawal.amount, Decimal("50.00"))
        self.assertEqual(withdrawal.status, "pending")

    def test_withdrawal_cannot_exceed_available_balance(self):
        self.profile.reserved_balance = Decimal("175.00")
        self.profile.save(update_fields=["reserved_balance"])

        response = self.client.post(
            reverse("request_withdrawal"),
            self.withdrawal_data("50.00"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            WithdrawalRequest.objects.filter(user=self.user).count(),
            0,
        )

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.reserved_balance, Decimal("175.00"))

    def test_minimum_withdrawal_is_50(self):
        response = self.client.post(
            reverse("request_withdrawal"),
            self.withdrawal_data("49.99"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            WithdrawalRequest.objects.filter(user=self.user).count(),
            0,
        )

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.reserved_balance, Decimal("0.00"))

    def test_available_balance_uses_reserved_balance(self):
        self.profile.reserved_balance = Decimal("75.00")
        self.profile.save(update_fields=["reserved_balance"])

        response = self.client.get(reverse("wallet"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["available_balance"],
            Decimal("125.00"),
        )

    def test_nan_withdrawal_is_rejected(self):
        response = self.client.post(
            reverse("request_withdrawal"),
            self.withdrawal_data("NaN"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            WithdrawalRequest.objects.filter(user=self.user).count(),
            0,
        )

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.reserved_balance, Decimal("0.00"))

    def test_infinity_withdrawal_is_rejected(self):
        response = self.client.post(
            reverse("request_withdrawal"),
            self.withdrawal_data("Infinity"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            WithdrawalRequest.objects.filter(user=self.user).count(),
            0,
        )

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.reserved_balance, Decimal("0.00"))

    def test_withdrawal_rejects_more_than_two_decimal_places(self):
        response = self.client.post(
            reverse("request_withdrawal"),
            self.withdrawal_data("50.001"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            WithdrawalRequest.objects.filter(user=self.user).count(),
            0,
        )

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.reserved_balance, Decimal("0.00"))

    def test_zero_withdrawal_is_rejected(self):
        response = self.client.post(
            reverse("request_withdrawal"),
            self.withdrawal_data("0"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            WithdrawalRequest.objects.filter(user=self.user).count(),
            0,
        )

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.reserved_balance, Decimal("0.00"))

    def test_negative_withdrawal_is_rejected(self):
        response = self.client.post(
            reverse("request_withdrawal"),
            self.withdrawal_data("-50.00"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            WithdrawalRequest.objects.filter(user=self.user).count(),
            0,
        )

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.reserved_balance, Decimal("0.00"))

    def test_empty_withdrawal_is_rejected(self):
        response = self.client.post(
            reverse("request_withdrawal"),
            self.withdrawal_data(""),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            WithdrawalRequest.objects.filter(user=self.user).count(),
            0,
        )

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.reserved_balance, Decimal("0.00"))

    def test_non_numeric_withdrawal_is_rejected(self):
        response = self.client.post(
            reverse("request_withdrawal"),
            self.withdrawal_data("abc"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            WithdrawalRequest.objects.filter(user=self.user).count(),
            0,
        )

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.reserved_balance, Decimal("0.00"))


class WithdrawalModelTests(TestCase):
    def test_withdrawal_defaults_to_pending(self):
        user = User.objects.create_user(username="withdrawal_user")

        withdrawal = WithdrawalRequest.objects.create(
            user=user,
            amount=Decimal("50.00"),
            bank_name="Test Bank",
            account_holder="Test Worker",
            bank_account="1234567890",
        )

        self.assertEqual(withdrawal.status, "pending")


class WithdrawalAdminActionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="admin_flow_worker",
            password="test-password-123",
        )
        AccountEntity.objects.create(
            user=self.user,
            entity_type=AccountEntity.EntityType.WORKER,
        )
        self.profile = WorkerProfile.objects.create(
            user=self.user,
            balance=Decimal("200.00"),
            reserved_balance=Decimal("50.00"),
            total_earned=Decimal("200.00"),
        )

        class ModelAdminStub:
            def message_user(self, request, message, level=None):
                pass

        self.modeladmin = ModelAdminStub()

        self.admin_user = User.objects.create_superuser(
            username="wallet_test_admin",
            password="test-admin-password-123",
        )
        self.payer_user = User.objects.create_user(
            username="wallet_test_payer",
            password="test-payer-password-123",
        )
        self.payer_user.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="wallet",
                codename="mark_withdrawal_paid",
            )
        )

        class RequestStub:
            pass

        self.request = RequestStub()
        self.request.user = self.admin_user

    def create_withdrawal(self, status="pending", amount="50.00"):
        return WithdrawalRequest.objects.create(
            user=self.user,
            amount=Decimal(amount),
            bank_name="Test Bank",
            account_holder="Test Worker",
            bank_account="1234567890",
            status=status,
        )

    def test_approve_withdrawal_keeps_reservation(self):
        withdrawal = self.create_withdrawal()
        approve_withdrawals(
            self.modeladmin,
            self.request,
            WithdrawalRequest.objects.filter(pk=withdrawal.pk),
        )
        withdrawal.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(withdrawal.status, "approved")
        self.assertEqual(self.profile.reserved_balance, Decimal("50.00"))
        self.assertEqual(self.profile.balance, Decimal("200.00"))

    def test_approve_already_approved_is_noop(self):
        withdrawal = self.create_withdrawal(status="approved")
        approve_withdrawals(
            self.modeladmin,
            self.request,
            WithdrawalRequest.objects.filter(pk=withdrawal.pk),
        )
        withdrawal.refresh_from_db()
        self.assertEqual(withdrawal.status, "approved")

    def test_reject_already_approved_is_noop(self):
        withdrawal = self.create_withdrawal(status="approved")
        reject_withdrawals(
            self.modeladmin,
            self.request,
            WithdrawalRequest.objects.filter(pk=withdrawal.pk),
        )
        withdrawal.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(withdrawal.status, "approved")
        self.assertEqual(self.profile.reserved_balance, Decimal("50.00"))

    def test_reject_already_rejected_is_noop(self):
        withdrawal = self.create_withdrawal(status="rejected")
        self.profile.reserved_balance = Decimal("0.00")
        self.profile.save(update_fields=["reserved_balance"])
        reject_withdrawals(
            self.modeladmin,
            self.request,
            WithdrawalRequest.objects.filter(pk=withdrawal.pk),
        )
        withdrawal.refresh_from_db()
        self.assertEqual(withdrawal.status, "rejected")

    def test_pay_pending_withdrawal_is_noop(self):
        self._use_payer()
        withdrawal = self.create_withdrawal(status="pending")
        mark_withdrawals_paid(
            self.modeladmin,
            self.request,
            WithdrawalRequest.objects.filter(pk=withdrawal.pk),
        )
        withdrawal.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(withdrawal.status, "pending")
        self.assertEqual(self.profile.balance, Decimal("200.00"))
        self.assertEqual(self.profile.reserved_balance, Decimal("50.00"))
        self.assertFalse(
            WalletTransaction.objects.filter(withdrawal=withdrawal).exists()
        )

    def test_approve_withdrawal_requires_reserved_balance(self):
        self.profile.reserved_balance = Decimal("0.00")
        self.profile.save(update_fields=["reserved_balance"])
        withdrawal = self.create_withdrawal()
        approve_withdrawals(
            self.modeladmin,
            self.request,
            WithdrawalRequest.objects.filter(pk=withdrawal.pk),
        )
        withdrawal.refresh_from_db()
        self.assertEqual(withdrawal.status, "pending")

    def test_reject_withdrawal_releases_reservation(self):
        withdrawal = self.create_withdrawal()
        reject_withdrawals(
            self.modeladmin,
            self.request,
            WithdrawalRequest.objects.filter(pk=withdrawal.pk),
        )
        withdrawal.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(withdrawal.status, "rejected")
        self.assertEqual(self.profile.reserved_balance, Decimal("0.00"))
        self.assertEqual(self.profile.balance, Decimal("200.00"))

    def _use_payer(self):
        self.request.user = self.payer_user

    def test_paid_withdrawal_deducts_balance_and_reservation(self):
        self._use_payer()
        withdrawal = self.create_withdrawal(status="approved")
        mark_withdrawals_paid(
            self.modeladmin,
            self.request,
            WithdrawalRequest.objects.filter(pk=withdrawal.pk),
        )
        withdrawal.refresh_from_db()
        self.profile.refresh_from_db()
        transaction = WalletTransaction.objects.get(
            user=self.user,
            transaction_type="withdrawal",
        )
        self.assertEqual(withdrawal.status, "paid")
        self.assertEqual(self.profile.balance, Decimal("150.00"))
        self.assertEqual(self.profile.reserved_balance, Decimal("0.00"))
        self.assertEqual(transaction.amount, Decimal("50.00"))
        self.assertEqual(transaction.description, f"Withdrawal #{withdrawal.id}")

    def test_paid_withdrawal_is_idempotent(self):
        self._use_payer()
        withdrawal = self.create_withdrawal(status="approved")
        mark_withdrawals_paid(
            self.modeladmin,
            self.request,
            WithdrawalRequest.objects.filter(pk=withdrawal.pk),
        )
        self.profile.refresh_from_db()
        first_balance = self.profile.balance
        first_reserved = self.profile.reserved_balance
        first_transactions = WalletTransaction.objects.filter(
            user=self.user,
            transaction_type="withdrawal",
        ).count()
        mark_withdrawals_paid(
            self.modeladmin,
            self.request,
            WithdrawalRequest.objects.filter(pk=withdrawal.pk),
        )
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.balance, first_balance)
        self.assertEqual(self.profile.reserved_balance, first_reserved)
        self.assertEqual(
            WalletTransaction.objects.filter(
                user=self.user,
                transaction_type="withdrawal",
            ).count(),
            first_transactions,
        )

    def test_paid_withdrawal_with_existing_matching_transaction_is_completed(self):
        self._use_payer()
        self.profile.balance = Decimal("150.00")
        self.profile.reserved_balance = Decimal("0.00")
        self.profile.save(update_fields=["balance", "reserved_balance"])
        withdrawal = self.create_withdrawal(status="approved")
        WalletTransaction.objects.create(
            user=self.user,
            amount=withdrawal.amount,
            transaction_type="withdrawal",
            description=f"Withdrawal #{withdrawal.id}",
        )
        mark_withdrawals_paid(
            self.modeladmin,
            self.request,
            WithdrawalRequest.objects.filter(pk=withdrawal.pk),
        )
        withdrawal.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(withdrawal.status, "paid")
        self.assertEqual(self.profile.balance, Decimal("150.00"))
        self.assertEqual(self.profile.reserved_balance, Decimal("0.00"))
        self.assertEqual(
            WalletTransaction.objects.filter(
                user=self.user,
                transaction_type="withdrawal",
            ).count(),
            1,
        )

    def test_reject_withdrawal_without_reservation_keeps_pending(self):
        self.profile.reserved_balance = Decimal("0.00")
        self.profile.save(update_fields=["reserved_balance"])
        withdrawal = self.create_withdrawal()
        reject_withdrawals(
            self.modeladmin,
            self.request,
            WithdrawalRequest.objects.filter(pk=withdrawal.pk),
        )
        withdrawal.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(withdrawal.status, "pending")
        self.assertEqual(self.profile.reserved_balance, Decimal("0.00"))

    def test_paid_withdrawal_without_reservation_stays_approved(self):
        self._use_payer()
        self.profile.reserved_balance = Decimal("0.00")
        self.profile.save(update_fields=["reserved_balance"])
        withdrawal = self.create_withdrawal(status="approved")
        mark_withdrawals_paid(
            self.modeladmin,
            self.request,
            WithdrawalRequest.objects.filter(pk=withdrawal.pk),
        )
        withdrawal.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(withdrawal.status, "approved")
        self.assertEqual(self.profile.balance, Decimal("200.00"))
        self.assertEqual(self.profile.reserved_balance, Decimal("0.00"))
        self.assertEqual(
            WalletTransaction.objects.filter(
                user=self.user,
                transaction_type="withdrawal",
            ).count(),
            0,
        )

    def test_paid_withdrawal_without_enough_balance_stays_approved(self):
        self._use_payer()
        self.profile.balance = Decimal("40.00")
        self.profile.reserved_balance = Decimal("40.00")
        self.profile.save(update_fields=["balance", "reserved_balance"])
        withdrawal = self.create_withdrawal(status="approved")
        mark_withdrawals_paid(
            self.modeladmin,
            self.request,
            WithdrawalRequest.objects.filter(pk=withdrawal.pk),
        )
        withdrawal.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(withdrawal.status, "approved")
        self.assertEqual(self.profile.balance, Decimal("40.00"))
        self.assertEqual(self.profile.reserved_balance, Decimal("40.00"))
        self.assertEqual(
            WalletTransaction.objects.filter(
                user=self.user,
                transaction_type="withdrawal",
            ).count(),
            0,
        )

    def test_already_paid_with_wrong_amount_stays_approved(self):
        self._use_payer()
        withdrawal = self.create_withdrawal(status="approved", amount="50.00")
        WalletTransaction.objects.create(
            user=self.user,
            amount=Decimal("40.00"),
            transaction_type="withdrawal",
            description=f"Withdrawal #{withdrawal.id}",
        )
        mark_withdrawals_paid(
            self.modeladmin,
            self.request,
            WithdrawalRequest.objects.filter(pk=withdrawal.pk),
        )
        withdrawal.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(withdrawal.status, "approved")
        self.assertEqual(self.profile.balance, Decimal("200.00"))
        self.assertEqual(self.profile.reserved_balance, Decimal("50.00"))


class WithdrawalAdminDataMinimizationTests(TestCase):
    def setUp(self):
        from django.test import RequestFactory
        from wallet.admin import WithdrawalRequestAdmin

        self.factory = RequestFactory()
        self.admin_site = admin.site
        self.model_admin = WithdrawalRequestAdmin(
            WithdrawalRequest,
            self.admin_site,
        )
        self.worker = User.objects.create_user(
            username="sensitive_worker",
            password="test-password-123",
        )
        self.withdrawal = WithdrawalRequest.objects.create(
            user=self.worker,
            amount=Decimal("75.00"),
            bank_name="Safe Bank",
            account_holder="Sensitive Person",
            bank_account="1234567890123456",
        )

    def request_for(self, user):
        request = self.factory.get("/admin/wallet/withdrawalrequest/")
        request.user = user
        return request

    def test_unprivileged_staff_cannot_view_withdrawal_admin(self):
        staff = User.objects.create_user(
            username="limited_staff",
            password="test-password-123",
            is_staff=True,
        )
        staff.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="wallet",
                codename="view_withdrawalrequest",
            )
        )
        self.assertFalse(
            self.model_admin.has_view_permission(
                self.request_for(staff),
                self.withdrawal,
            )
        )

    def test_finance_can_view_withdrawal_admin(self):
        finance = User.objects.create_user(
            username="finance_viewer",
            password="test-password-123",
            is_staff=True,
        )
        finance.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="wallet",
                codename="approve_withdrawal",
            )
        )
        self.assertTrue(
            self.model_admin.has_view_permission(
                self.request_for(finance),
                self.withdrawal,
            )
        )

    def test_payer_can_view_withdrawal_admin(self):
        payer = User.objects.create_user(
            username="payer_viewer",
            password="test-password-123",
            is_staff=True,
        )
        payer.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="wallet",
                codename="mark_withdrawal_paid",
            )
        )
        self.assertTrue(
            self.model_admin.has_view_permission(
                self.request_for(payer),
                self.withdrawal,
            )
        )

    def test_superuser_can_view_withdrawal_admin(self):
        owner = User.objects.create_superuser(
            username="withdrawal_owner",
            password="test-password-123",
        )
        self.assertTrue(
            self.model_admin.has_view_permission(
                self.request_for(owner),
                self.withdrawal,
            )
        )

    def test_admin_list_masks_sensitive_payment_identity(self):
        masked_account = self.model_admin.masked_bank_account(self.withdrawal)
        masked_holder = self.model_admin.masked_account_holder(self.withdrawal)

        self.assertNotEqual(masked_account, self.withdrawal.bank_account)
        self.assertNotIn(self.withdrawal.bank_account, masked_account)
        self.assertEqual(masked_account, "••••3456")
        self.assertNotEqual(masked_holder, self.withdrawal.account_holder)
        self.assertNotIn(self.withdrawal.account_holder, masked_holder)
        self.assertEqual(masked_holder, "S•••")

    def test_admin_search_excludes_raw_payment_identifiers(self):
        self.assertNotIn("bank_account", self.model_admin.search_fields)
        self.assertNotIn("account_holder", self.model_admin.search_fields)

    def test_admin_detail_excludes_raw_payment_identifiers(self):
        self.assertNotIn("bank_account", self.model_admin.readonly_fields)
        self.assertNotIn("account_holder", self.model_admin.readonly_fields)
        self.assertIn("masked_bank_account", self.model_admin.readonly_fields)
        self.assertIn("masked_account_holder", self.model_admin.readonly_fields)


class WithdrawalHistoryDataMinimizationTests(TestCase):
    def test_worker_history_does_not_render_raw_payment_identifiers(self):
        user = User.objects.create_user(username="history_worker", password="test-password-123")
        AccountEntity.objects.create(user=user, entity_type=AccountEntity.EntityType.WORKER)
        WorkerProfile.objects.create(user=user, balance=Decimal("100.00"), reserved_balance=Decimal("50.00"), total_earned=Decimal("100.00"))
        WithdrawalRequest.objects.create(
            user=user, amount=Decimal("50.00"), bank_name="Safe Bank",
            account_holder="Sensitive Person", bank_account="1234567890123456",
        )
        self.client.force_login(user)
        response = self.client.get(reverse("withdrawal_history"))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertNotIn("1234567890123456", content)
        self.assertNotIn("Sensitive Person", content)
        self.assertIn("••••3456", content)
        self.assertIn("S•••", content)


class WithdrawalOperationIdentityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="operation_identity_worker",
            password="test-password-123",
        )
        self.withdrawal = WithdrawalRequest.objects.create(
            user=self.user,
            amount=Decimal("75.00"),
            bank_name="Safe Bank",
            account_holder="Worker",
            bank_account="1234567890",
            status="paid",
        )

    def test_withdrawal_ledger_entry_binds_to_exact_operation(self):
        transaction = WalletTransaction.objects.create(
            user=self.user,
            amount=self.withdrawal.amount,
            transaction_type="withdrawal",
            description=f"Withdrawal #{self.withdrawal.id}",
            withdrawal=self.withdrawal,
        )

        self.assertEqual(transaction.withdrawal_id, self.withdrawal.id)
        self.assertEqual(self.withdrawal.wallet_transaction.pk, transaction.pk)

    def test_task_identity_requires_earning_transaction_type(self):
        task = Task.objects.create(
            title="Identity Task",
            description="Test task",
            reward=Decimal("25.00"),
        )
        claim = TaskClaim.objects.create(
            task=task,
            worker=self.user,
            status="approved",
        )

        with self.assertRaises(IntegrityError):
            WalletTransaction.objects.create(
                user=self.user,
                amount=Decimal("25.00"),
                transaction_type="withdrawal",
                description="Invalid task identity",
                task_claim=claim,
            )

    def test_promotion_identity_requires_earning_transaction_type(self):
        promotion = Promotion.objects.create(
            title="Identity Promotion",
            description="Test promotion",
            advertiser_name="Test Advertiser",
            reward=Decimal("25.00"),
        )
        claim = PromotionClaim.objects.create(
            promotion=promotion,
            worker=self.user,
            status="approved",
        )

        with self.assertRaises(IntegrityError):
            WalletTransaction.objects.create(
                user=self.user,
                amount=Decimal("25.00"),
                transaction_type="withdrawal",
                description="Invalid promotion identity",
                promotion_claim=claim,
            )

    def test_withdrawal_identity_requires_withdrawal_transaction_type(self):
        with self.assertRaises(IntegrityError):
            WalletTransaction.objects.create(
                user=self.user,
                amount=Decimal("75.00"),
                transaction_type="earning",
                description="Invalid withdrawal identity",
                withdrawal=self.withdrawal,
            )

    def test_multiple_operation_identities_are_rejected(self):
        task = Task.objects.create(
            title="Multi Identity Task",
            description="Test task",
            reward=Decimal("25.00"),
        )
        claim = TaskClaim.objects.create(
            task=task,
            worker=self.user,
            status="approved",
        )

        with self.assertRaises(IntegrityError):
            WalletTransaction.objects.create(
                user=self.user,
                amount=Decimal("75.00"),
                transaction_type="withdrawal",
                description="Multiple operation identities",
                task_claim=claim,
                withdrawal=self.withdrawal,
            )

    def test_second_ledger_entry_for_same_withdrawal_is_rejected(self):
        WalletTransaction.objects.create(
            user=self.user,
            amount=self.withdrawal.amount,
            transaction_type="withdrawal",
            description=f"Withdrawal #{self.withdrawal.id}",
            withdrawal=self.withdrawal,
        )

        with self.assertRaises(IntegrityError):
            WalletTransaction.objects.create(
                user=self.user,
                amount=self.withdrawal.amount,
                transaction_type="withdrawal",
                description=f"Withdrawal #{self.withdrawal.id}",
                withdrawal=self.withdrawal,
            )
