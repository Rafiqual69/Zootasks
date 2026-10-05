from django.contrib import admin, messages
from django.db import transaction
from django.utils import timezone
import logging

from .models import Promotion, PromotionClaim
from accounts.models import WorkerProfile
from wallet.models import WalletTransaction
from core.security_policy_engine import require_authorized

logger = logging.getLogger(__name__)


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "advertiser_name",
        "reward",
        "budget",
        "max_workers",
        "completed_workers",
        "status",
        "created_at",
    )
    list_filter = ("status",)
    search_fields = ("title", "advertiser_name")

    # Protected promotion financial/state fields are read-only in generic admin forms.
    readonly_fields = ("reward", "budget", "max_workers", "completed_workers", "status")


@admin.register(PromotionClaim)
class PromotionClaimAdmin(admin.ModelAdmin):
    list_display = (
        "promotion",
        "worker",
        "status",
        "claimed_at",
        "submitted_at",
        "approved_at",
    )
    list_filter = ("status",)
    search_fields = (
        "promotion__title",
        "worker__username",
    )

    readonly_fields = (
        "promotion",
        "worker",
        "proof",
        "status",
        "claimed_at",
        "submitted_at",
        "approved_at",
    )

    actions = ["approve_claims", "reject_claims"]

    def has_view_permission(self, request, obj=None):
        user = request.user
        if not user.is_authenticated or not user.is_staff:
            return False
        if user.is_superuser:
            return True
        return any(
            user.has_perm(permission)
            for permission in (
                "promotions.approve_promotion_claim",
                "promotions.reject_promotion_claim",
            )
        )

    @admin.action(description="Approve selected promotion claims and pay reward")
    def approve_claims(self, request, queryset):
        if not request.user.has_perm("promotions.approve_promotion_claim"):
            self.message_user(
                request,
                "You do not have permission to approve promotion claims.",
                messages.ERROR,
            )
            return

        paid = 0
        already_paid = 0
        failed = 0

        for claim_id in queryset.values_list("id", flat=True):
            try:
                with transaction.atomic():
                    locked = (
                        PromotionClaim.objects
                        .select_for_update()
                        .select_related("promotion", "worker")
                        .get(id=claim_id)
                    )

                    require_authorized(actor="finance", resource="promotion_claim", action="approve", scope="role_scope", facts={"permission.promotion_approve": True, "business_rules.valid_promotion_claim": locked.status == "submitted"})

                    if locked.status != "submitted":
                        continue

                    existing_payment = WalletTransaction.objects.filter(
                        promotion_claim=locked,
                        transaction_type="earning",
                    ).first()

                    if existing_payment:
                        if locked.status != "approved":
                            locked.status = "approved"
                            locked.approved_at = (
                                locked.approved_at or timezone.now()
                            )
                            locked.save(
                                update_fields=[
                                    "status",
                                    "approved_at",
                                ]
                            )

                        already_paid += 1
                        continue

                    profile = (
                        WorkerProfile.objects
                        .select_for_update()
                        .get(user=locked.worker)
                    )

                    reward = locked.promotion.reward

                    profile.balance += reward
                    profile.total_earned += reward
                    profile.save(
                        update_fields=[
                            "balance",
                            "total_earned",
                        ]
                    )

                    WalletTransaction.objects.create(
                        user=locked.worker,
                        amount=reward,
                        transaction_type="earning",
                        description=(
                            f"Promotion reward: "
                            f"{locked.promotion.title}"
                        ),
                        promotion_claim=locked,
                    )

                    locked.status = "approved"
                    locked.approved_at = timezone.now()
                    locked.save(
                        update_fields=[
                            "status",
                            "approved_at",
                        ]
                    )

                    paid += 1

            except Exception:
                logger.exception("Promotion claim approval failed safely")
                failed += 1

        if paid:
            self.message_user(
                request,
                f"{paid} promotion reward(s) approved and credited.",
                messages.SUCCESS,
            )

        if already_paid:
            self.message_user(
                request,
                (
                    f"{already_paid} promotion claim(s) were already paid. "
                    "No duplicate payment made."
                ),
                messages.WARNING,
            )

        if failed:
            self.message_user(
                request,
                f"{failed} promotion claim(s) failed safely.",
                messages.ERROR,
            )

        if not paid and not already_paid and not failed:
            self.message_user(
                request,
                "No submitted promotion claims were available.",
                messages.INFO,
            )

    @admin.action(description="Reject selected promotion claims")
    def reject_claims(self, request, queryset):
        if not request.user.has_perm("promotions.reject_promotion_claim"):
            self.message_user(
                request,
                "You do not have permission to reject promotion claims.",
                messages.ERROR,
            )
            return

        updated = 0
        for claim_id in queryset.values_list("id", flat=True):
            with transaction.atomic():
                claim = PromotionClaim.objects.select_for_update().get(id=claim_id)
                require_authorized(actor="finance", resource="promotion_claim", action="reject", scope="role_scope", facts={"permission.promotion_reject": True, "business_rules.valid_promotion_claim": claim.status == "submitted"})
                if claim.status != "submitted":
                    continue
                claim.status = "rejected"
                claim.approved_at = None
                claim.save(update_fields=["status", "approved_at"])
                updated += 1

        self.message_user(
            request,
            f"{updated} promotion claim(s) rejected.",
            messages.WARNING,
        )
