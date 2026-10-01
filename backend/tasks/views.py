from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import Task, TaskClaim
from .services import (
    TaskServiceError,
    claim_task_for_worker,
    submit_claim_proof,
)


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
            task.max_workers - task.claimed_workers,
            0,
        )
        task.progress_percent = min(
            (task.claimed_workers / max(task.max_workers, 1)) * 100,
            100,
        )

    context = {
        "tasks": task_list,
        "categories": list(categories)[:5],
        "selected_category": category,
    }

    return render(request, "tasks/marketplace.html", context)


@login_required
def claim_task(request, task_id):
    if request.method != "POST":
        return redirect("task_marketplace")

    try:
        claim_task_for_worker(user=request.user, task_id=task_id)
    except TaskServiceError:
        pass

    return redirect("task_marketplace")


@login_required
def task_detail(request, task_id):
    return redirect("task_marketplace")


@login_required
def submit_task(request, task_id):
    claim = TaskClaim.objects.filter(
        task_id=task_id,
        worker=request.user,
    ).first()

    if claim is None:
        from django.http import Http404
        raise Http404

    if request.method == "POST":
        try:
            submit_claim_proof(
                user=request.user,
                task_id=task_id,
                proof=request.POST.get("proof", ""),
            )
        except TaskServiceError:
            pass
        else:
            return redirect("task_marketplace")

    claim.refresh_from_db()
    if claim.status != "claimed":
        return redirect("task_marketplace")

    return render(
        request,
        "tasks/submit_task.html",
        {"claim": claim},
    )
