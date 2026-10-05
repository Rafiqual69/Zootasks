from django.contrib import admin, messages
from django.db import transaction
from django.utils import timezone
import logging

from .models import Promotion, PromotionClaim
from accounts.models import AccountEntity, WorkerProfile
from wallet.models import WalletTransaction
from core.security_policy_engine import authorize, require_authorized

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

    financial_immutable_fields = ("reward", "budget", "max_workers", "completed_workers")

    # Protected promotion financial/state fields are read-only in generic admin forms.
    readonly_fields = ("reward", "budget", "max_workers", "completed_workers", "status")

    def _owner_policy_facts(self, request, obj=None):
        user = request.user
        owner_boundary = (
            bool(user and user.is_authenticated and user.is_staff and user.is_superuser)
            and AccountEntity.objects.filter(
                user=user,
                entity_type=AccountEntity.EntityType.OWNER,
                is_active=True,
            ).exists()
        )
        facts = {
            "owner_authenticated": bool(user and user.is_authenticated),
            "canonical_owner_boundary": owner_boundary,
            "admin_request": True,
        }
        if obj is not None:
            facts["admin_protected_fields_immutable"] = (
                set(self.get_readonly_fields(request, obj))
                >= set(self.financial_immutable_fields + ("status",))
            )
        return facts

    def has_add_permission(self, request):
        return authorize(
            actor="owner",
            resource="promotion",
            action="create",
            scope="global",
            facts=self._owner_policy_facts(request),
        )

    def has_change_permission(self, request, obj=None):
        return authorize(
            actor="owner",
            resource="promotion",
            action="update",
            scope="global",
            facts=self._owner_policy_facts(request, obj),
        )

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return ()
        return self.financial_immutable_fields + ("status",)


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

                    if locked.status != "submitted":
                        continue

                    require_authorized(actor="finance", resource="promotion_claim", action="approve", scope="role_scope", facts={"permission.promotion_approve": True, "business_rules.valid_promotion_claim": True})

                    reward = locked.promotion.reward
                    existing_payment = WalletTransaction.objects.filter(
                        promotion_claim=locked,
                        transaction_type="earning",
                    ).first()

                    if existing_payment:
                        if existing_payment.amount != reward:
                            self.message_user(
                                request,
                                f"❌ Promotion claim #{locked.id} skipped: existing ledger amount does not match the current reward. Manual reconciliation required.",
                                messages.ERROR,
                            )
                            continue
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

            except Exception as exc:
                # Never emit exception tracebacks here: traceback/local-variable
                # rendering can expose sensitive request or object data. Keep the
                # operational event bounded to non-sensitive metadata only.
                logger.error(
                    "Promotion claim approval failed safely: %s",
                    type(exc).__name__,
                    extra={
                        "security_event": "promotion_claim_approval_failure",
                        "claim_id": claim_id,
                    },
                    exc_info=False,
                )
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
                if claim.status != "submitted":
                    continue
                require_authorized(actor="finance", resource="promotion_claim", action="reject", scope="role_scope", facts={"permission.promotion_reject": True, "business_rules.valid_promotion_claim": True})
                claim.status = "rejected"
                claim.approved_at = None
                claim.save(update_fields=["status", "approved_at"])
                updated += 1

        self.message_user(
            request,
            f"{updated} promotion claim(s) rejected.",
            messages.WARNING,
        )
