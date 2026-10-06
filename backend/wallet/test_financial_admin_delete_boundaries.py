from django.contrib import admin
from django.test import SimpleTestCase

from promotions.admin import PromotionClaimAdmin
from promotions.models import PromotionClaim
from tasks.admin import TaskClaimAdmin
from tasks.models import TaskClaim
from wallet.admin import WalletTransactionAdmin, WithdrawalRequestAdmin
from wallet.models import WalletTransaction, WithdrawalRequest


class FinancialAdminDeleteBoundaryTests(SimpleTestCase):
    def test_wallet_transaction_admin_disables_destructive_writes(self):
        model_admin = WalletTransactionAdmin(WalletTransaction, admin.site)
        request = object()

        self.assertFalse(model_admin.has_add_permission(request))
        self.assertFalse(model_admin.has_change_permission(request))
        self.assertFalse(model_admin.has_delete_permission(request))

    def test_withdrawal_admin_disables_destructive_writes(self):
        model_admin = WithdrawalRequestAdmin(WithdrawalRequest, admin.site)
        request = object()

        self.assertFalse(model_admin.has_add_permission(request))
        self.assertFalse(model_admin.has_change_permission(request))
        self.assertFalse(model_admin.has_delete_permission(request))

    def test_task_claim_admin_blocks_add_and_delete(self):
        model_admin = TaskClaimAdmin(TaskClaim, admin.site)
        request = object()

        self.assertFalse(model_admin.has_add_permission(request))
        self.assertFalse(model_admin.has_delete_permission(request))

    def test_promotion_claim_admin_blocks_add_and_delete(self):
        model_admin = PromotionClaimAdmin(PromotionClaim, admin.site)
        request = object()

        self.assertFalse(model_admin.has_add_permission(request))
        self.assertFalse(model_admin.has_delete_permission(request))
