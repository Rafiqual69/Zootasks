from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.middleware.csrf import get_token
from django.middleware.csrf import get_token
from .models import Task, TaskClaim

@login_required
def marketplace(request):
    tasks = Task.objects.filter(status="active").order_by("-created_at")
    categories = Task.objects.filter(status="active").values_list("category", flat=True).distinct()
    category = request.GET.get("category", "").strip()
    if category:
        tasks = tasks.filter(category=category)
    cards = ""
    for task in tasks:
        claim = TaskClaim.objects.filter(task=task, worker=request.user).first()
        remaining = max(task.max_workers - task.completed_workers, 0)
        if claim:
            if claim.status == "claimed":
                action = f'<a class="btn-action" href="/tasks/{task.id}/submit/">📤 Submit</a>'
            elif claim.status == "submitted":
                action = '<div class="status-badge waiting">⏳ Review</div>'
            elif claim.status == "approved":
                action = '<div class="status-badge success">✅ Done</div>'
            else:
                action = '<div class="status-badge danger">❌ Rejected</div>'
        elif remaining > 0:
            action = f'<form method="post" action="/tasks/{task.id}/claim/" style="margin:0"><input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}"><button class="btn-action" type="submit">🎯 Claim</button></form>'
        else:
            action = '<div class="status-badge">🔒 Full</div>'
        progress = (task.completed_workers / max(task.max_workers, 1)) * 100
        cards += f"""<div class="task-card">
            <div class="task-header"><span class="category-tag">{task.category}</span><div class="task-reward">৳{task.reward}</div></div>
            <h3>{task.title}</h3><p class="task-desc">{task.description[:80]}...</p>
            <div class="progress-bar"><div class="progress-fill" style="width:{progress}%"></div></div>
            <p class="progress-text">{task.completed_workers}/{task.max_workers}</p>
            <div class="task-action">{action}</div></div>"""
    if not cards:
        cards = '<div class="empty-state"><h2>📋 No tasks</h2></div>'
    filters = ''.join([f'<a href="/tasks/?category={cat}">{cat}</a>' for cat in list(categories)[:5]])
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tasks - ZooTasks</title>
<style>*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:system-ui;background:#f8fafc;color:#0f172a}}header{{background:linear-gradient(135deg,#2563eb,#7c3aed);color:white;padding:16px 0;position:sticky;top:0}}header .container{{max-width:1200px;margin:0 auto;padding:0 16px;display:flex;justify-content:space-between}}.logo{{font-size:20px;font-weight:bold}}.header-nav{{display:flex;gap:20px}}.header-nav a{{color:white;text-decoration:none;opacity:.9}}.header-nav a:hover{{opacity:1}}.container{{max-width:1200px;margin:0 auto;padding:0 16px}}.hero{{background:linear-gradient(135deg,#2563eb,#7c3aed);color:white;padding:40px 16px;text-align:center}}.hero h1{{font-size:32px;margin-bottom:12px}}.filters{{display:flex;gap:12px;margin:30px 0;flex-wrap:wrap;justify-content:center}}.filters a{{padding:8px 16px;border-radius:20px;background:white;color:#2563eb;border:2px solid #2563eb;cursor:pointer;font-weight:600;font-size:13px;text-decoration:none;transition:all .2s}}.filters a:hover{{background:#2563eb;color:white}}.content{{padding:40px 16px}}.tasks-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px;margin-top:30px}}.task-card{{background:white;border-radius:14px;padding:20px;box-shadow:0 1px 3px rgba(0,0,0,.08);border:1px solid #e2e8f0;transition:transform .2s}}.task-card:hover{{transform:translateY(-4px);box-shadow:0 12px 24px rgba(0,0,0,.12)}}.task-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}}.category-tag{{background:#e0e7ff;color:#2563eb;padding:4px 10px;border-radius:6px;font-size:11px;font-weight:600}}.task-reward{{font-size:20px;font-weight:bold;color:#16a34a}}.task-card h3{{font-size:16px;margin-bottom:8px;line-height:1.3}}.task-desc{{color:#64748b;font-size:13px;margin-bottom:14px}}.progress-bar{{height:6px;background:#e2e8f0;border-radius:10px;overflow:hidden;margin-bottom:6px}}.progress-fill{{height:100%;background:linear-gradient(90deg,#2563eb,#7c3aed)}}.progress-text{{font-size:11px;color:#94a3b8;margin-bottom:14px}}.btn-action{{width:100%;padding:10px;background:#2563eb;color:white;border:none;border-radius:8px;font-weight:600;font-size:13px;cursor:pointer;text-decoration:none;text-align:center;display:block;transition:all .2s}}.btn-action:hover{{background:#1d4ed8}}.status-badge{{padding:6px 10px;border-radius:6px;font-size:11px;font-weight:600;text-align:center}}.status-badge.waiting{{background:#fef3c7;color:#92400e}}.status-badge.success{{background:#dcfce7;color:#166534}}.status-badge.danger{{background:#fee2e2;color:#991b1b}}.empty-state{{text-align:center;padding:60px 20px;color:#94a3b8}}@media(max-width:768px){{.tasks-grid{{grid-template-columns:1fr}}}}</style>
</head><body>
<header><div class="container"><div class="logo">🦁 ZooTasks</div><div class="header-nav"><a href="/accounts/dashboard/">Dashboard</a><a href="/promotions/">Promos</a><a href="/">Home</a></div></div></header>
<div class="hero"><div class="container"><h1>📋 Tasks</h1></div></div>
<div class="content"><div class="container"><div class="filters"><a href="/tasks/">All</a>{filters}</div><div class="tasks-grid">{cards}</div></div></div>
</body></html>"""
    return HttpResponse(html)

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
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Submit - ZooTasks</title>
<style>*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:system-ui;background:linear-gradient(135deg,#f8fafc,#e0e7ff);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}}.box{{background:white;border-radius:20px;padding:40px;box-shadow:0 20px 60px rgba(0,0,0,.15);max-width:600px;width:100%}}.box h1{{font-size:28px;margin-bottom:8px;color:#2563eb}}.box h2{{font-size:20px;color:#0f172a;margin-bottom:12px;margin-top:24px}}.box p{{color:#64748b;margin-bottom:20px;line-height:1.6}}textarea{{width:100%;min-height:160px;padding:16px;border:2px solid #e2e8f0;border-radius:12px;font-family:inherit;font-size:14px}}textarea:focus{{outline:none;border-color:#2563eb}}button{{width:100%;padding:14px;background:linear-gradient(135deg,#2563eb,#7c3aed);color:white;border:none;border-radius:12px;font-weight:600;font-size:16px;cursor:pointer;margin-top:20px;transition:transform .2s,box-shadow .2s}}button:hover{{transform:translateY(-2px);box-shadow:0 10px 20px rgba(37,99,235,.3)}}</style>
</head><body>
<div class="box"><h1>📤 Submit Task</h1><h2>{claim.task.title}</h2><p>{claim.task.description}</p>
<form method="post"><input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}"><textarea name="proof" placeholder="Describe completion..." required></textarea><button type="submit">✓ Submit</button></form></div>
</body></html>"""
    return HttpResponse(html)
