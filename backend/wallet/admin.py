from django.contrib import admin, messages
from django.db import transaction
from django.utils import timezone
from accounts.models import WorkerProfile

from .models import WalletTransaction, WithdrawalRequest


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "amount",
        "transaction_type",
        "description",
        "created_at",
    )

    list_filter = (
        "transaction_type",
        "created_at",
    )

    search_fields = (
        "user__username",
        "description",
    )

    readonly_fields = (
        "user",
        "amount",
        "transaction_type",
        "description",
        "task_claim",
        "promotion_claim",
        "created_at",
    )


@admin.action(description="✅ Approve selected withdrawals")
def approve_withdrawals(modeladmin, request, queryset):
    if not request.user.has_perm("wallet.approve_withdrawal"):
        modeladmin.message_user(
            request,
            "You do not have permission to approve withdrawals.",
            messages.ERROR,
        )
        return

    updated = 0
    skipped = 0

    for withdrawal_id in queryset.values_list("id", flat=True):
        with transaction.atomic():
            withdrawal = (
                WithdrawalRequest.objects
                .select_for_update()
                .get(id=withdrawal_id)
            )

            if withdrawal.status != "pending":
                skipped += 1
                continue

            profile = (
                WorkerProfile.objects
                .select_for_update()
                .get(user=withdrawal.user)
            )

            if profile.reserved_balance < withdrawal.amount:
                skipped += 1
                modeladmin.message_user(
                    request,
                    f"❌ Withdrawal #{withdrawal.id} skipped: "
                    f"reserved balance ৳{profile.reserved_balance} "
                    f"is less than withdrawal ৳{withdrawal.amount}.",
                    messages.ERROR,
                )
                continue

            withdrawal.status = "approved"
            withdrawal.processed_at = timezone.now()
            withdrawal.save(
                update_fields=["status", "processed_at"]
            )
            updated += 1

    if updated:
        modeladmin.message_user(
            request,
            f"{updated} withdrawal request(s) approved.",
            messages.SUCCESS,
        )

    if skipped:
        modeladmin.message_user(
            request,
            f"{skipped} withdrawal request(s) skipped.",
            messages.WARNING,
        )


@admin.action(description="❌ Reject selected withdrawals")
def reject_withdrawals(modeladmin, request, queryset):
    if not request.user.has_perm("wallet.reject_withdrawal"):
        modeladmin.message_user(
            request,
            "You do not have permission to reject withdrawals.",
            messages.ERROR,
        )
        return

    updated = 0

    for withdrawal_id in queryset.values_list("id", flat=True):
        with transaction.atomic():
            withdrawal = (
                WithdrawalRequest.objects
                .select_for_update()
                .get(id=withdrawal_id)
            )

            if withdrawal.status != "pending":
                continue

            profile = (
                WorkerProfile.objects
                .select_for_update()
                .get(user=withdrawal.user)
            )

            if profile.reserved_balance < withdrawal.amount:
                continue

            profile.reserved_balance -= withdrawal.amount
            profile.save(update_fields=["reserved_balance"])

            withdrawal.status = "rejected"
            withdrawal.processed_at = timezone.now()
            withdrawal.save(
                update_fields=["status", "processed_at"]
            )
            updated += 1

    modeladmin.message_user(
        request,
        f"{updated} withdrawal request(s) rejected.",
        messages.WARNING,
    )


@admin.action(description="💵 Mark selected withdrawals as PAID")
def mark_withdrawals_paid(modeladmin, request, queryset):
    if not request.user.has_perm("wallet.mark_withdrawal_paid"):
        modeladmin.message_user(
            request,
            "You do not have permission to mark withdrawals as paid.",
            messages.ERROR,
        )
        return

    paid_count = 0
    skipped_count = 0

    for withdrawal_id in queryset.values_list("id", flat=True):

        with transaction.atomic():

            withdrawal = (
                WithdrawalRequest.objects
                .select_for_update()
                .select_related("user")
                .get(id=withdrawal_id)
            )

            if withdrawal.status != "approved":
                skipped_count += 1
                continue

            existing_transaction = (
                WalletTransaction.objects
                .filter(
                    user=withdrawal.user,
                    transaction_type="withdrawal",
                    description=f"Withdrawal #{withdrawal.id}",
                )
                .first()
            )

            if existing_transaction:
                if existing_transaction.amount != withdrawal.amount:
                    skipped_count += 1
                    modeladmin.message_user(
                        request,
                        f"❌ Withdrawal #{withdrawal.id} skipped: "
                        f"existing transaction amount "
                        f"৳{existing_transaction.amount} does not match "
                        f"withdrawal ৳{withdrawal.amount}. "
                        f"Manual reconciliation required.",
                        messages.ERROR,
                    )
                    continue

                withdrawal.status = "paid"
                withdrawal.processed_at = (
                    withdrawal.processed_at or timezone.now()
                )
                withdrawal.save(
                    update_fields=[
                        "status",
                        "processed_at",
                    ]
                )
                paid_count += 1
                continue

            profile = (
                WorkerProfile.objects
                .select_for_update()
                .get(user=withdrawal.user)
            )

            amount = withdrawal.amount

            if profile.reserved_balance < amount:
                skipped_count += 1
                modeladmin.message_user(
                    request,
                    f"❌ Withdrawal #{withdrawal.id} skipped: "
                    f"reserved balance ৳{profile.reserved_balance} "
                    f"is less than withdrawal ৳{amount}.",
                    messages.ERROR,
                )
                continue

            if profile.balance < amount:
                skipped_count += 1
                modeladmin.message_user(
                    request,
                    f"❌ Withdrawal #{withdrawal.id} skipped: "
                    f"balance ৳{profile.balance} is less than "
                    f"withdrawal ৳{amount}.",
                    messages.ERROR,
                )
                continue

            WalletTransaction.objects.create(
                user=withdrawal.user,
                amount=amount,
                transaction_type="withdrawal",
                description=f"Withdrawal #{withdrawal.id}",
            )

            profile.balance -= amount
            profile.reserved_balance -= amount
            profile.save(
                update_fields=[
                    "balance",
                    "reserved_balance",
                ]
            )

            withdrawal.status = "paid"
            withdrawal.processed_at = timezone.now()

            withdrawal.save(
                update_fields=[
                    "status",
                    "processed_at",
                ]
            )

            paid_count += 1

    if paid_count:
        modeladmin.message_user(
            request,
            f"{paid_count} withdrawal(s) marked as paid and wallet updated.",
            messages.SUCCESS,
        )

    if skipped_count:
        modeladmin.message_user(
            request,
            f"{skipped_count} withdrawal(s) skipped because they were not ready or already paid.",
            messages.WARNING,
        )


@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "amount",
        "bank_name",
        "account_holder",
        "bank_account",
        "status",
        "requested_at",
        "processed_at",
    )

    list_filter = (
        "status",
        "bank_name",
        "requested_at",
    )

    search_fields = (
        "user__username",
        "bank_name",
        "account_holder",
        "bank_account",
    )

    ordering = (
        "-requested_at",
    )

    actions = [
        approve_withdrawals,
        reject_withdrawals,
        mark_withdrawals_paid,
    ]

    readonly_fields = (
        "user",
        "amount",
        "bank_name",
        "account_holder",
        "bank_account",
        "status",
        "requested_at",
        "processed_at",
    )
