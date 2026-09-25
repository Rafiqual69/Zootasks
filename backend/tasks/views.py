from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .models import Task, TaskClaim

@login_required
def marketplace(request):
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

@login_required
@transaction.atomic
def claim_task(request, task_id):
    if request.method != "POST":
        return redirect("task_marketplace")
    task = get_object_or_404(Task.objects.select_for_update(), id=task_id, status="active")
    existing = TaskClaim.objects.filter(task=task, worker=request.user).first()
    if existing or task.completed_workers >= task.max_workers:
        return redirect("task_marketplace")
    TaskClaim.objects.create(task=task, worker=request.user)
    task.completed_workers += 1
    if task.completed_workers >= task.max_workers:
        task.status = "completed"
    task.save(update_fields=["completed_workers", "status"])
    return redirect("task_marketplace")

@login_required
def task_detail(request, task_id):
    return redirect("task_marketplace")

@login_required
def submit_task(request, task_id):
    claim = get_object_or_404(TaskClaim, task_id=task_id, worker=request.user)
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
