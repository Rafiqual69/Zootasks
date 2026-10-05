from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.authorization import worker_required
from core.security_policy_engine import require_authorized
from .models import Task, TaskClaim


@worker_required
def marketplace(request):
    require_authorized(
        actor="worker", resource="task", action="read", scope="role_scope",
        facts={"account_entity.active_worker": True},
    )
    category = request.GET.get("category", "").strip()

    tasks = Task.objects.filter(status="active").order_by("-created_at")

    if category:
        tasks = tasks.filter(category=category)

    categories = (
        Task.objects
        .filter(status="active")
        .values_list("category", flat=True)
        .distinct()
        .order_by("category")
    )

    task_list = list(tasks)

    claims = TaskClaim.objects.filter(
        task_id__in=[task.id for task in task_list],
        worker=request.user,
    )

    claims_by_task = {claim.task_id: claim for claim in claims}

    for task in task_list:
        task.worker_claim = claims_by_task.get(task.id)
        task.remaining_workers = max(
            task.max_workers - task.completed_workers,
            0,
        )
        task.progress_percent = min(
            (task.completed_workers / max(task.max_workers, 1)) * 100,
            100,
        )

    context = {
        "tasks": task_list,
        "categories": list(categories)[:5],
        "selected_category": category,
    }

    return render(request, "tasks/marketplace.html", context)


@worker_required
@transaction.atomic
def claim_task(request, task_id):
    require_authorized(
        actor="worker", resource="task", action="claim", scope="role_scope",
        facts={
            "account_entity.active_worker": True,
            "task.active": True,
            "task.capacity_available": True,
            "request.method.POST": request.method == "POST",
        },
    )
    if request.method != "POST":
        return redirect("task_marketplace")
    task = get_object_or_404(
        Task.objects.select_for_update(),
        id=task_id,
        status="active",
    )
    existing = TaskClaim.objects.filter(
        task=task,
        worker=request.user,
    ).first()
    if existing or task.completed_workers >= task.max_workers:
        return redirect("task_marketplace")
    TaskClaim.objects.create(task=task, worker=request.user)
    task.completed_workers += 1
    if task.completed_workers >= task.max_workers:
        task.status = "completed"
    task.save(update_fields=["completed_workers", "status"])
    return redirect("task_marketplace")


@worker_required
def task_detail(request, task_id):
    return redirect("task_marketplace")


@worker_required
def submit_task(request, task_id):
    claim = get_object_or_404(
        TaskClaim,
        task_id=task_id,
        worker=request.user,
    )
    require_authorized(
        actor="worker", resource="task_claim", action="submit",
        scope="own",
        facts={
            "account_entity.active_worker": True,
            "object.owner_is_actor": claim.worker_id == request.user.id,
            "claim.status.claimed": claim.status == "claimed",
            "request.method.POST": request.method == "POST",
        },
    )
    if claim.status != "claimed":
        return redirect("task_marketplace")
    if request.method == "POST":
        proof = request.POST.get("proof", "").strip()
        if proof:
            claim.proof = proof
            claim.status = "submitted"
            claim.submitted_at = timezone.now()
            claim.save(update_fields=["proof", "status", "submitted_at"])
            return redirect("task_marketplace")
    return render(request, "tasks/submit_task.html", {"claim": claim})
