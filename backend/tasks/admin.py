from django.contrib import admin, messages
from django.db import transaction

from .models import Task, TaskClaim
from accounts.models import AccountEntity, WorkerProfile
from wallet.models import WalletTransaction
from core.security_policy_engine import authorize, require_authorized


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "reward",
        "completed_workers",
        "max_workers",
        "status",
        "deadline",
        "created_at",
    )
    list_filter = ("status", "category")
    search_fields = ("title", "description")
    ordering = ("-created_at",)

    financial_immutable_fields = ("reward", "max_workers", "completed_workers")

    # Protected task fields are never directly writable through generic Django
    # admin forms. Financial/state changes must use an explicit policy-bound workflow.
    readonly_fields = ("reward", "max_workers", "completed_workers", "status")

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
            resource="task",
            action="create",
            scope="global",
            facts=self._owner_policy_facts(request),
        )

    def has_change_permission(self, request, obj=None):
        return authorize(
            actor="owner",
            resource="task",
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


@admin.action(description="✅ Approve selected submissions & pay reward")
def approve_submissions(modeladmin, request, queryset):
    if not request.user.has_perm("tasks.approve_task_submission"):
        modeladmin.message_user(
            request,
            "You do not have permission to approve task submissions.",
            messages.ERROR,
        )
        return

    approved = 0
    already_paid = 0

    for claim_id in queryset.values_list("id", flat=True):
        with transaction.atomic():
            claim = (
                TaskClaim.objects
                .select_for_update()
                .select_related("task", "worker")
                .get(id=claim_id)
            )

            if claim.status != "submitted":
                continue

            require_authorized(actor="finance", resource="task_claim", action="approve", scope="role_scope", facts={"permission.task_approve": True, "business_rules.valid_task_claim": True})

            reward = claim.task.reward
            existing_payment = WalletTransaction.objects.filter(
                task_claim=claim,
                transaction_type="earning",
            ).first()

            if existing_payment:
                if existing_payment.amount != reward:
                    modeladmin.message_user(
                        request,
                        f"❌ Task claim #{claim.id} skipped: existing ledger amount does not match the current reward. Manual reconciliation required.",
                        messages.ERROR,
                    )
                    continue
                claim.status = "approved"
                claim.save(update_fields=["status"])
                already_paid += 1
                continue

            profile = (
                WorkerProfile.objects
                .select_for_update()
                .get(user=claim.worker)
            )

            profile.balance += reward
            profile.total_earned += reward
            profile.completed_tasks += 1

            profile.save(
                update_fields=[
                    "balance",
                    "total_earned",
                    "completed_tasks",
                ]
            )

            WalletTransaction.objects.create(
                user=claim.worker,
                amount=reward,
                transaction_type="earning",
                description=f"Reward for: {claim.task.title}",
                task_claim=claim,
            )

            claim.status = "approved"
            claim.save(update_fields=["status"])

            approved += 1

    if approved:
        modeladmin.message_user(
            request,
            f"{approved} submission(s) approved and rewarded.",
            messages.SUCCESS,
        )

    if already_paid:
        modeladmin.message_user(
            request,
            f"{already_paid} submission(s) were already paid. "
            "No duplicate payment made.",
            messages.WARNING,
        )

    if not approved and not already_paid:
        modeladmin.message_user(
            request,
            "No submitted submissions were available for approval.",
            messages.INFO,
        )


@admin.action(description="❌ Reject selected submissions")
def reject_submissions(modeladmin, request, queryset):
    if not request.user.has_perm("tasks.reject_task_submission"):
        modeladmin.message_user(
            request,
            "You do not have permission to reject task submissions.",
            messages.ERROR,
        )
        return

    updated = 0
    for claim_id in queryset.values_list("id", flat=True):
        with transaction.atomic():
            claim = TaskClaim.objects.select_for_update().get(id=claim_id)
            if claim.status != "submitted":
                continue
            require_authorized(actor="finance", resource="task_claim", action="reject", scope="role_scope", facts={"permission.task_reject": True, "business_rules.valid_task_claim": True})
            claim.status = "rejected"
            claim.save(update_fields=["status"])
            updated += 1

    modeladmin.message_user(
        request,
        f"{updated} submission(s) rejected.",
        messages.WARNING,
    )


@admin.register(TaskClaim)
class TaskClaimAdmin(admin.ModelAdmin):
    list_display = (
        "task",
        "worker",
        "status",
        "reward_amount",
        "claimed_at",
        "submitted_at",
        "payment_status",
    )

    list_filter = (
        "status",
        "claimed_at",
        "submitted_at",
    )

    search_fields = (
        "task__title",
        "worker__username",
    )

    ordering = ("-claimed_at",)

    actions = [
        approve_submissions,
        reject_submissions,
    ]

    readonly_fields = (
        "task",
        "worker",
        "proof",
        "status",
        "claimed_at",
        "submitted_at",
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
                "tasks.approve_task_submission",
                "tasks.reject_task_submission",
            )
        )

    @admin.display(description="Reward")
    def reward_amount(self, obj):
        return f"৳{obj.task.reward}"

    @admin.display(description="Payment")
    def payment_status(self, obj):
        if hasattr(obj, "wallet_transaction"):
            return "💰 Paid"
        if obj.status == "submitted":
            return "⏳ Awaiting Review"
        if obj.status == "approved":
            return "⚠️ Approved / Payment Missing"
        if obj.status == "rejected":
            return "❌ Rejected"
        return "—"
