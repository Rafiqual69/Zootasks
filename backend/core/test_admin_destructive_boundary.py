from types import SimpleNamespace

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import RequestFactory, SimpleTestCase

from promotions.admin import PromotionClaimAdmin
from promotions.models import PromotionClaim
from tasks.admin import TaskClaimAdmin
from tasks.models import TaskClaim
from wallet.admin import WithdrawalRequestAdmin, WalletTransactionAdmin
from wallet.models import WalletTransaction, WithdrawalRequest


class FinancialAdminDestructiveBoundaryTests(SimpleTestCase):
    def setUp(self):
        self.request = RequestFactory().get("/admin/")
        self.request.user = SimpleNamespace(
            id=1,
            is_authenticated=True,
            is_staff=True,
            is_superuser=True,
        )

    def test_financial_history_delete_is_denied(self):
        for model, admin_class in (
            (WalletTransaction, WalletTransactionAdmin),
            (WithdrawalRequest, WithdrawalRequestAdmin),
            (TaskClaim, TaskClaimAdmin),
            (PromotionClaim, PromotionClaimAdmin),
        ):
            instance = admin_class(model, admin.site)
            self.assertFalse(instance.has_delete_permission(self.request))
