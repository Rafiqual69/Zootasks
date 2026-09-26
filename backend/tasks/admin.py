from django.contrib import admin, messages
from accounts.policies import is_owner
from django.db import transaction

from .models import Task, TaskClaim
from accounts.models import WorkerProfile
from wallet.models import WalletTransaction


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Only the canonical active Owner may create financial root objects.
        return is_owner(request.user)

    def has_delete_permission(self, request, obj=None):
        # Tasks are financial/audit roots; archive via status instead of deleting.
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            # Owner may create a new task with its initial reward/capacity.
            return ("completed_workers", "created_at")

        # Existing task reward/capacity/lifecycle state must not be changed
        # through a generic admin form. Controlled application flows own these
        # state transitions.
        return (
            "reward",
            "max_workers",
            "completed_workers",
            "status",
            "created_at",
        )

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

            existing_payment = WalletTransaction.objects.filter(
                task_claim=claim
            ).first()

            if existing_payment:
                claim.status = "approved"
                claim.save(update_fields=["status"])
                already_paid += 1
                continue

            reward = claim.task.reward

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
            claim = (
                TaskClaim.objects
                .select_for_update()
                .get(id=claim_id)
            )

            if claim.status != "submitted":
                continue

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
    def has_delete_permission(self, request, obj=None):
        # Claims participate in payout/audit history and must not be deleted.
        return False

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
        "proof",
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
