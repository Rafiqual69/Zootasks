from django.contrib import admin, messages
from accounts.policies import is_owner

from .models import Task, TaskClaim
from .services import (
    TaskServiceError,
    approve_claim,
    reject_claim,
)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return is_owner(request.user)

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return ("claimed_workers", "completed_workers", "created_at")

        return (
            "reward",
            "max_workers",
            "claimed_workers",
            "completed_workers",
            "status",
            "created_at",
        )

    list_display = (
        "title",
        "category",
        "reward",
        "claimed_workers",
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
        try:
            _, result = approve_claim(claim_id=claim_id)
        except TaskServiceError:
            continue

        if result == "approved":
            approved += 1
        elif result == "already_paid":
            already_paid += 1
        elif result == "already_approved":
            already_paid += 1

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
        try:
            _, result = reject_claim(claim_id=claim_id)
        except TaskServiceError:
            continue

        if result in {"rejected", "already_rejected"}:
            updated += 1

    modeladmin.message_user(
        request,
        f"{updated} submission(s) rejected.",
        messages.WARNING,
    )


@admin.register(TaskClaim)
class TaskClaimAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
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
