from django.db import transaction
from django.db.models import F
from django.utils import timezone

from accounts.models import WorkerProfile
from wallet.models import WalletTransaction

from .models import Task, TaskClaim


class TaskServiceError(Exception):
    """Expected business-rule failure in the task lifecycle."""


@transaction.atomic
def claim_task_for_worker(*, user, task_id):
    task = (
        Task.objects
        .select_for_update()
        .filter(id=task_id, status="active")
        .first()
    )
    if task is None:
        raise TaskServiceError("task_unavailable")

    if task.claimed_workers >= task.max_workers:
        raise TaskServiceError("task_full")

    claim = (
        TaskClaim.objects
        .select_for_update()
        .filter(task=task, worker=user)
        .first()
    )

    if claim is not None and claim.status != "rejected":
        raise TaskServiceError("already_claimed")

    if claim is None:
        claim = TaskClaim.objects.create(
            task=task,
            worker=user,
            status="claimed",
        )
    else:
        claim.status = "claimed"
        claim.proof = ""
        claim.submitted_at = None
        claim.claimed_at = timezone.now()
        claim.save(
            update_fields=[
                "status",
                "proof",
                "submitted_at",
                "claimed_at",
            ]
        )

    task.claimed_workers = F("claimed_workers") + 1
    task.save(update_fields=["claimed_workers"])
    task.refresh_from_db(fields=["claimed_workers"])

    return claim


@transaction.atomic
def submit_claim_proof(*, user, task_id, proof):
    proof = (proof or "").strip()
    if not proof:
        raise TaskServiceError("proof_required")

    claim = (
        TaskClaim.objects
        .select_for_update()
        .filter(task_id=task_id, worker=user)
        .first()
    )
    if claim is None:
        raise TaskServiceError("claim_not_found")

    if claim.status != "claimed":
        raise TaskServiceError("claim_not_submittable")

    claim.proof = proof
    claim.status = "submitted"
    claim.submitted_at = timezone.now()
    claim.save(update_fields=["proof", "status", "submitted_at"])
    return claim


@transaction.atomic
def approve_claim(*, claim_id):
    claim = (
        TaskClaim.objects
        .select_for_update()
        .select_related("task", "worker")
        .filter(id=claim_id)
        .first()
    )
    if claim is None:
        raise TaskServiceError("claim_not_found")

    if claim.status == "approved":
        return claim, "already_approved"

    if claim.status != "submitted":
        raise TaskServiceError("claim_not_submittable")

    task = Task.objects.select_for_update().get(pk=claim.task_id)
    profile, _ = (
        WorkerProfile.objects
        .select_for_update()
        .get_or_create(user=claim.worker)
    )

    existing_payment = WalletTransaction.objects.filter(
        task_claim=claim,
        transaction_type="earning",
    ).first()

    if existing_payment is None:
        WalletTransaction.objects.create(
            user=claim.worker,
            amount=task.reward,
            transaction_type="earning",
            description=f"Reward for: {task.title}",
            task_claim=claim,
        )
        profile.balance += task.reward
        profile.total_earned += task.reward
        profile.completed_tasks += 1
        profile.save(
            update_fields=[
                "balance",
                "total_earned",
                "completed_tasks",
            ]
        )
        result = "approved"
    else:
        result = "already_paid"

    claim.status = "approved"
    claim.save(update_fields=["status"])

    Task.objects.filter(
        pk=task.pk,
        completed_workers__lt=F("max_workers"),
    ).update(
        completed_workers=F("completed_workers") + 1,
    )

    task.refresh_from_db(fields=["completed_workers", "max_workers", "status"])
    if task.completed_workers >= task.max_workers:
        task.status = "completed"
        task.save(update_fields=["status"])

    return claim, result


@transaction.atomic
def reject_claim(*, claim_id):
    claim = (
        TaskClaim.objects
        .select_for_update()
        .select_related("task")
        .filter(id=claim_id)
        .first()
    )
    if claim is None:
        raise TaskServiceError("claim_not_found")

    if claim.status == "rejected":
        return claim, "already_rejected"

    if claim.status != "submitted":
        raise TaskServiceError("claim_not_rejectable")

    task = Task.objects.select_for_update().get(pk=claim.task_id)

    claim.status = "rejected"
    claim.save(update_fields=["status"])

    Task.objects.filter(
        pk=task.pk,
        claimed_workers__gt=0,
    ).update(
        claimed_workers=F("claimed_workers") - 1,
    )

    task.refresh_from_db(fields=["claimed_workers", "completed_workers", "max_workers", "status"])
    if (
        task.status == "completed"
        and task.completed_workers < task.max_workers
    ):
        task.status = "active"
        task.save(update_fields=["status"])

    return claim, "rejected"
