from django.contrib import admin, messages
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
import logging

from .models import Promotion, PromotionClaim
from accounts.models import AccountEntity, WorkerProfile
from wallet.models import WalletTransaction
from core.security_policy_engine import authorize
from core.execution_authorization import require_execution_authorized

logger = logging.getLogger(__name__)


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "advertiser_name",
        "reward",
        "budget",
        "max_workers",
        "reserved_workers",
        "completed_workers",
        "status",
        "created_at",
    )
    list_filter = ("status",)
    search_fields = ("title", "advertiser_name")

    financial_immutable_fields = (
        "reward",
        "budget",
        "max_workers",
        "reserved_workers",
        "completed_workers",
    )

    # Protected promotion financial/state fields are read-only in generic admin forms.
    readonly_fields = (
        "reward",
        "budget",
        "max_workers",
        "reserved_workers",
        "completed_workers",
        "status",
    )

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
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


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
        return authorize(
            actor="finance",
            resource="promotion_claim",
            action="read",
            scope="role_scope",
            facts={
                "permission.promotion_review": (user.has_perm("promotions.approve_promotion_claim") or user.has_perm("promotions.reject_promotion_claim")),
            },
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

                    require_execution_authorized(
                        request=request,
                        operation="promotion_claim.approve",
                        target=f"promotion_claim:{locked.id}",
                        scope="role_scope",
                        material_parameters={
                            "claim_id": locked.id,
                            "reward": str(locked.promotion.reward),
                            "status": locked.status,
                        },
                        actor="finance",
                        resource="promotion_claim",
                        action="approve",
                        authorization_scope="role_scope",
                        authorization_facts={
                            "permission.promotion_approve": True,
                            "business_rules.valid_promotion_claim": True,
                        },
                    )

                    promotion = (
                        Promotion.objects
                        .select_for_update()
                        .get(id=locked.promotion_id)
                    )
                    reward = promotion.reward

                    if promotion.completed_workers >= promotion.reserved_workers:
                        self.message_user(
                            request,
                            f"❌ Promotion claim #{locked.id} cannot be approved: no uncompleted reservation remains. Manual reconciliation required.",
                            messages.ERROR,
                        )
                        continue

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

                        promotion.completed_workers += 1
                        promotion.save(update_fields=["completed_workers"])

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

                    approved_payout_total = (
                        WalletTransaction.objects
                        .filter(
                            promotion_id=promotion.id,
                            transaction_type="earning",
                        )
                        .aggregate(total=Sum("amount"))
                        .get("total")
                        or reward.__class__("0.00")
                    )
                    if approved_payout_total + reward > promotion.budget:
                        self.message_user(
                            request,
                            (
                                f"❌ Promotion claim #{locked.id} cannot be approved: "
                                "promotion budget would be exceeded. Manual reconciliation required."
                            ),
                            messages.ERROR,
                        )
                        continue

                    profile = (
                        WorkerProfile.objects
                        .select_for_update()
                        .get(user=locked.worker)
                    )

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
                            f"{promotion.title}"
                        ),
                        promotion_claim=locked,
                    )

                    promotion.completed_workers += 1
                    promotion.save(update_fields=["completed_workers"])

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
                claim = (
                    PromotionClaim.objects
                    .select_for_update()
                    .get(id=claim_id)
                )
                if claim.status != "submitted":
                    continue

                require_execution_authorized(
                    request=request,
                    operation="promotion_claim.reject",
                    target=f"promotion_claim:{claim.id}",
                    scope="role_scope",
                    material_parameters={
                        "claim_id": claim.id,
                        "status": claim.status,
                    },
                    actor="finance",
                    resource="promotion_claim",
                    action="reject",
                    authorization_scope="role_scope",
                    authorization_facts={
                        "permission.promotion_reject": True,
                        "business_rules.valid_promotion_claim": True,
                    },
                )

                promotion = (
                    Promotion.objects
                    .select_for_update()
                    .get(id=claim.promotion_id)
                )
                if promotion.reserved_workers <= 0:
                    self.message_user(
                        request,
                        f"❌ Promotion claim #{claim.id} has no reservation to release; manual reconciliation required.",
                        messages.ERROR,
                    )
                    continue

                promotion.reserved_workers -= 1
                if (
                    promotion.status == "paused"
                    and promotion.reserved_workers < promotion.max_workers
                ):
                    promotion.status = "active"
                promotion.save(update_fields=["reserved_workers", "status"])

                claim.status = "rejected"
                claim.approved_at = None
                claim.save(update_fields=["status", "approved_at"])
                updated += 1

        self.message_user(
            request,
            f"{updated} promotion claim(s) rejected.",
            messages.WARNING,
        )
