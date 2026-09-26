from django.conf import settings
from django.contrib import admin, messages
from django.db import transaction
from django.utils import timezone

from .models import Promotion, PromotionClaim
from accounts.models import WorkerProfile
from wallet.models import WalletTransaction


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Only the configured Owner may create financial root objects.
        owner_username = getattr(settings, "OWNER_USERNAME", "")
        return (
            bool(owner_username)
            and request.user.is_superuser
            and request.user.get_username() == owner_username
        )

    def has_delete_permission(self, request, obj=None):
        # Promotions are financial/audit roots; use status transitions instead.
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            # Owner may create a new promotion with its initial reward/budget
            # and capacity. Runtime lifecycle counters remain protected.
            return ("completed_workers", "status", "created_at")

        return (
            "reward",
            "budget",
            "max_workers",
            "completed_workers",
            "status",
            "created_at",
        )

    list_display = (
        "title",
        "advertiser_name",
        "advertiser",
        "reward",
        "budget",
        "max_workers",
        "completed_workers",
        "status",
        "created_at",
    )
    list_filter = ("status",)
    search_fields = (
        "title",
        "advertiser_name",
        "advertiser__organization_name",
        "advertiser__user__username",
    )


@admin.register(PromotionClaim)
class PromotionClaimAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        # Claims participate in payout/audit history and must not be deleted.
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

                claim.status = "rejected"
                claim.approved_at = None
                claim.save(
                    update_fields=[
                        "status",
                        "approved_at",
                    ]
                )
                updated += 1

        self.message_user(
            request,
            f"{updated} promotion claim(s) rejected.",
            messages.WARNING,
        )
