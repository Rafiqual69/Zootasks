from django.contrib import admin
from django.db import transaction
from django.utils import timezone

from .models import Promotion, PromotionClaim
from wallet.models import WalletTransaction


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

    actions = ["approve_claims", "reject_claims"]

    @admin.action(description="Approve selected promotion claims and pay reward")
    def approve_claims(self, request, queryset):
        paid = 0

        for claim in queryset.select_related("promotion", "worker"):
            if claim.status != "submitted":
                continue

            with transaction.atomic():
                locked = PromotionClaim.objects.select_for_update().get(
                    id=claim.id
                )

                if locked.status != "submitted":
                    continue

                WalletTransaction.objects.create(
                    user=locked.worker,
                    amount=locked.promotion.reward,
                    transaction_type="earning",
                    description=f"Promotion reward: {locked.promotion.title}",
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

        self.message_user(
            request,
            f"{paid} promotion reward(s) approved and credited."
        )

    @admin.action(description="Reject selected promotion claims")
    def reject_claims(self, request, queryset):
        updated = queryset.filter(
            status="submitted"
        ).update(status="rejected")

        self.message_user(
            request,
            f"{updated} promotion claim(s) rejected."
        )
