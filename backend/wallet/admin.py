from django.contrib import admin, messages
from django.db import transaction
from django.utils import timezone
from accounts.models import WorkerProfile

from .models import WalletTransaction, WithdrawalRequest
from core.critical_execution import require_execution_authorized


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
        "withdrawal",
        "created_at",
    )

    def has_view_permission(self, request, obj=None):
        user = request.user
        if not user.is_authenticated or not user.is_staff:
            return False
        if user.is_superuser:
            return True
        return any(
            user.has_perm(permission)
            for permission in (
                "wallet.approve_withdrawal",
                "wallet.reject_withdrawal",
                "wallet.mark_withdrawal_paid",
            )
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

            # Terminal/replayed states are safe no-ops. Check state before
            # policy evaluation so a replay does not require an authorization
            # context for an operation that will not execute.
            if withdrawal.status != "pending":
                skipped += 1
                continue

            require_execution_authorized(
                request=request,
                actor="finance",
                operation="withdrawal.approve",
                target=f"withdrawal:{withdrawal.id}",
                resource="withdrawal",
                action="approve",
                material_parameters={
                    "withdrawal_id": withdrawal.id,
                    "user_id": withdrawal.user_id,
                    "amount": str(withdrawal.amount),
                    "status": withdrawal.status,
                },
                authorization_facts={
                    "permission.withdrawal_approve": True,
                    "business_rules.valid_withdrawal": True,
                },
            )

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

            require_execution_authorized(
                request=request,
                actor="finance",
                operation="withdrawal.reject",
                target=f"withdrawal:{withdrawal.id}",
                resource="withdrawal",
                action="reject",
                material_parameters={
                    "withdrawal_id": withdrawal.id,
                    "user_id": withdrawal.user_id,
                    "amount": str(withdrawal.amount),
                    "status": withdrawal.status,
                },
                authorization_facts={
                    "permission.withdrawal_reject": True,
                    "business_rules.pending_withdrawal": True,
                },
            )

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

            # A replay of an already-completed state is a no-op, not a new
            # protected payment operation. Never mutate it, but allow the
            # idempotent action to be safely skipped.
            if withdrawal.status != "approved":
                skipped_count += 1
                continue

            is_payer = (
                request.user.has_perm("wallet.mark_withdrawal_paid")
                and not request.user.has_perm("wallet.approve_withdrawal")
            )
            require_execution_authorized(
                request=request,
                actor="finance_payer",
                operation="withdrawal.pay",
                target=f"withdrawal:{withdrawal.id}",
                resource="withdrawal",
                action="pay",
                material_parameters={
                    "withdrawal_id": withdrawal.id,
                    "user_id": withdrawal.user_id,
                    "amount": str(withdrawal.amount),
                    "status": withdrawal.status,
                },
                authorization_facts={
                    "permission.withdrawal_pay": is_payer,
                    "business_rules.approved_withdrawal": True,
                    "idempotency.required": True,
                },
            )

            # The ledger entry must be bound to this exact withdrawal
            # operation by a DB-enforced OneToOne identity. Do not fall back
            # to description matching: descriptions are human-readable data,
            # not an authorization or idempotency key.
            existing_transaction = (
                WalletTransaction.objects
                .filter(withdrawal=withdrawal)
                .first()
            )

            # Transitional reconciliation for legacy rows created before
            # operation identity existed. The human-readable description is
            # accepted only as a migration bridge, never as the sole
            # authority: exact withdrawal id, user, type, and amount must all
            # match before the row is bound to this operation.
            if existing_transaction is None:
                legacy_transaction = (
                    WalletTransaction.objects
                    .filter(
                        user=withdrawal.user,
                        transaction_type="withdrawal",
                        description=f"Withdrawal #{withdrawal.id}",
                        withdrawal__isnull=True,
                    )
                    .first()
                )
                if legacy_transaction is not None:
                    if legacy_transaction.amount != withdrawal.amount:
                        skipped_count += 1
                        modeladmin.message_user(
                            request,
                            f"❌ Withdrawal #{withdrawal.id} skipped: "
                            "legacy ledger amount does not match withdrawal amount. "
                            "Manual reconciliation required.",
                            messages.ERROR,
                        )
                        continue
                    legacy_transaction.withdrawal = withdrawal
                    legacy_transaction.save(update_fields=["withdrawal"])
                    existing_transaction = legacy_transaction

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
                withdrawal=withdrawal,
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
        "masked_account_holder",
        "masked_bank_account",
        "status",
        "requested_at",
        "processed_at",
    )

    list_filter = (
        "status",
        "bank_name",
        "requested_at",
    )

    # Never support exact searching over sensitive payment identifiers.
    # Username/bank name are sufficient operational filters without exposing
    # raw account numbers or account-holder names through the admin search UX.
    search_fields = (
        "user__username",
        "bank_name",
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
        "masked_account_holder",
        "masked_bank_account",
        "status",
        "requested_at",
        "processed_at",
    )

    @staticmethod
    def _mask(value: str, visible_suffix: int = 0) -> str:
        if not value:
            return "—"
        value = str(value)
        if visible_suffix and len(value) > visible_suffix:
            return f"••••{value[-visible_suffix:]}"
        return "•" * min(max(len(value), 1), 12)

    @admin.display(description="Account holder")
    def masked_account_holder(self, obj):
        value = obj.account_holder or ""
        if not value:
            return "—"
        return f"{value[0]}•••"

    @admin.display(description="Bank account")
    def masked_bank_account(self, obj):
        return self._mask(obj.bank_account, visible_suffix=4)

    def has_view_permission(self, request, obj=None):
        user = request.user
        if not user.is_authenticated or not user.is_staff:
            return False
        if user.is_superuser:
            return True
        return any(
            user.has_perm(permission)
            for permission in (
                "wallet.approve_withdrawal",
                "wallet.reject_withdrawal",
                "wallet.mark_withdrawal_paid",
            )
        )
