#!/bin/bash

# Promotions URLs
cat > promotions/urls.py <<'PY'
from django.urls import path
from .views import marketplace, start_promotion, submit_promotion

urlpatterns = [
    path("", marketplace, name="promotion_marketplace"),
    path("<int:promotion_id>/start/", start_promotion, name="start_promotion"),
    path("<int:promotion_id>/submit/", submit_promotion, name="submit_promotion"),
]
PY

# Tasks URLs
cat > tasks/urls.py <<'PY'
from django.urls import path
from .views import marketplace, task_detail, claim_task, submit_task

urlpatterns = [
    path("", marketplace, name="task_marketplace"),
    path("<int:task_id>/", task_detail, name="task_detail"),
    path("<int:task_id>/claim/", claim_task, name="claim_task"),
    path("<int:task_id>/submit/", submit_task, name="submit_task"),
]
PY

# Accounts URLs
cat > accounts/urls.py <<'PY'
from django.contrib.auth.views import LogoutView
from django.urls import path
from .views import register, dashboard

urlpatterns = [
    path("register/", register, name="register"),
    path("dashboard/", dashboard, name="dashboard"),
    path("logout/", LogoutView.as_view(next_page="/"), name="logout"),
]
PY

# Main URLs
cat > main/urls.py <<'PY'
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path("", TemplateView.as_view(template_name="main/home.html"), name="home"),
]
PY

# Config URLs
cat > config/urls.py <<'PY'
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("tasks/", include("tasks.urls")),
    path("promotions/", include("promotions.urls")),
    path("", include("main.urls")),
]
PY

# Withdrawal Models
cat > wallet/models.py <<'PY'
from django.contrib.auth.models import User
from django.db import models


class WalletTransaction(models.Model):
    TRANSACTION_CHOICES = [
        ("earning", "Task Earning"),
        ("withdrawal", "Withdrawal"),
        ("adjustment", "Admin Adjustment"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wallet_transactions")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_CHOICES)
    description = models.CharField(max_length=255)
    task_claim = models.OneToOneField("tasks.TaskClaim", on_delete=models.SET_NULL, null=True, blank=True, related_name="wallet_transaction")
    promotion_claim = models.OneToOneField("promotions.PromotionClaim", on_delete=models.SET_NULL, null=True, blank=True, related_name="wallet_transaction")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - ৳{self.amount}"


class WithdrawalRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("paid", "Paid"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="withdrawal_requests")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    bank_account = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=100)
    account_holder = models.CharField(max_length=150)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-requested_at"]

    def __str__(self):
        return f"{self.user.username} - ৳{self.amount} ({self.status})"
PY

# Withdrawal Views
cat > wallet/views.py <<'PY'
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Sum
from django.utils import timezone

from .models import WalletTransaction, WithdrawalRequest


@login_required
def request_withdrawal(request):
    balance = (WalletTransaction.objects.filter(
        user=request.user, transaction_type="earning"
    ).aggregate(total=Sum("amount"))["total"] or 0) - (
        WalletTransaction.objects.filter(
        user=request.user, transaction_type="withdrawal"
    ).aggregate(total=Sum("amount"))["total"] or 0)

    if request.method == "POST":
        amount = request.POST.get("amount", "0")
        bank_account = request.POST.get("bank_account", "").strip()
        bank_name = request.POST.get("bank_name", "").strip()
        account_holder = request.POST.get("account_holder", "").strip()

        try:
            amount = float(amount)
            if amount > 0 and amount <= balance and bank_account and bank_name and account_holder:
                WithdrawalRequest.objects.create(
                    user=request.user,
                    amount=amount,
                    bank_account=bank_account,
                    bank_name=bank_name,
                    account_holder=account_holder,
                )
                return redirect("withdrawal_success")
        except:
            pass

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Withdrawal - ZooTasks</title>
        <style>
            * {{ box-sizing: border-box; }}
            body {{
                font-family: Arial, sans-serif;
                background: #f4f7fb;
                padding: 20px;
                margin: 0;
            }}
            .container {{ max-width: 600px; margin: auto; }}
            .box {{
                background: white;
                padding: 30px;
                border-radius: 20px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            }}
            .info {{
                background: #dbeafe;
                padding: 15px;
                border-radius: 12px;
                margin-bottom: 20px;
                color: #1e40af;
            }}
            input {{
                width: 100%;
                padding: 12px;
                margin-bottom: 15px;
                border: 1px solid #ddd;
                border-radius: 8px;
                font-size: 14px;
            }}
            button {{
                width: 100%;
                padding: 14px;
                background: #2563eb;
                color: white;
                border: 0;
                border-radius: 8px;
                font-weight: bold;
                cursor: pointer;
            }}
            button:hover {{ background: #1d4ed8; }}
            a {{ color: #2563eb; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="box">
                <h1>Request Withdrawal</h1>
                <div class="info">
                    <strong>Available Balance: ৳{balance}</strong>
                </div>
                <form method="post">
                    <input type="hidden" name="csrfmiddlewaretoken" value="{request.META.get('CSRF_COOKIE', '')}">
                    <input type="number" name="amount" placeholder="Amount (৳)" required>
                    <input type="text" name="bank_name" placeholder="Bank Name" required>
                    <input type="text" name="account_holder" placeholder="Account Holder Name" required>
                    <input type="text" name="bank_account" placeholder="Account Number" required>
                    <button type="submit">Request Withdrawal</button>
                </form>
                <p><a href="/accounts/dashboard/">← Back to Dashboard</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)


@login_required
def withdrawal_success(request):
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Withdrawal Requested</title>
        <style>
            body {{
                font-family: Arial;
                background: #f4f7fb;
                padding: 40px 20px;
                text-align: center;
            }}
            .box {{
                max-width: 500px;
                margin: auto;
                background: white;
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            }}
            h1 {{ color: #16a34a; }}
            a {{ color: #2563eb; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="box">
            <h1>✓ Withdrawal Requested</h1>
            <p>Your withdrawal request has been submitted. It will be processed within 2-3 business days.</p>
            <p><a href="/accounts/dashboard/">Go to Dashboard</a></p>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)
PY

# Wallet URLs
cat > wallet/urls.py <<'PY'
from django.urls import path
from .views import request_withdrawal, withdrawal_success

urlpatterns = [
    path("withdraw/", request_withdrawal, name="request_withdrawal"),
    path("withdraw/success/", withdrawal_success, name="withdrawal_success"),
]
PY

# Update Config URLs with wallet
sed -i "s|path(\"promotions/\",|path(\"wallet/\", include(\"wallet.urls\")),\n    path(\"promotions/\",|" config/urls.py

# Tasks Views - Full implementation
cat > tasks/views.py <<'PY'
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import TaskSubmissionForm
from .models import Task, TaskClaim


@login_required
def marketplace(request):
    tasks = Task.objects.filter(status="active").order_by("-created_at")
    claimed_ids = TaskClaim.objects.filter(worker=request.user).values_list("task_id", flat=True)

    cards = ""
    for task in tasks:
        remaining = max(task.max_workers - task.completed_workers, 0)
        claimed = task.id in claimed_ids
        
        if claimed:
            action = '<a class="btn" href="/tasks/{}/submit/">Submit Proof</a>'.format(task.id)
        elif remaining > 0:
            action = '<form method="post" action="/tasks/{}/claim/"><input type="hidden" name="csrfmiddlewaretoken" value="{}"><button class="btn" type="submit">Claim Task</button></form>'.format(task.id, request.META.get("CSRF_COOKIE", ""))
        else:
            action = '<div class="waiting">Task Full</div>'

        cards += f"""
        <div class="card">
            <div class="top">
                <span class="category">{task.category}</span>
                <span class="reward">৳{task.reward}</span>
            </div>
            <h2>{task.title}</h2>
            <p>{task.description}</p>
            <p><strong>Workers remaining:</strong> {remaining}</p>
            {action}
        </div>
        """

    if not cards:
        cards = '<div class="empty"><h2>No tasks available</h2></div>'

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Tasks - ZooTasks</title>
        <style>
            * {{ box-sizing: border-box; }}
            body {{
                margin: 0;
                padding: 20px;
                font-family: Arial, sans-serif;
                background: #f4f7fb;
            }}
            .container {{ max-width: 950px; margin: auto; }}
            .hero {{
                padding: 30px;
                border-radius: 24px;
                background: linear-gradient(135deg, #2563eb, #7c3aed);
                color: white;
                margin-bottom: 25px;
            }}
            .card {{
                background: white;
                padding: 22px;
                border-radius: 20px;
                margin-bottom: 18px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            }}
            .top {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 15px;
            }}
            .category {{
                background: #e0e7ff;
                color: #2563eb;
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
            }}
            .reward {{
                color: #16a34a;
                font-size: 18px;
                font-weight: bold;
            }}
            .btn {{
                display: block;
                width: 100%;
                padding: 12px;
                background: #2563eb;
                color: white;
                border: 0;
                border-radius: 10px;
                font-weight: bold;
                cursor: pointer;
            }}
            .waiting {{
                padding: 12px;
                background: #fef3c7;
                color: #92400e;
                border-radius: 10px;
                text-align: center;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="hero">
                <h1>Task Marketplace</h1>
                <p>Complete tasks and earn rewards</p>
            </div>
            <h2>Available Tasks ({len(tasks)})</h2>
            {cards}
            <p><a href="/accounts/dashboard/">← Back to Dashboard</a></p>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)


@login_required
@transaction.atomic
def claim_task(request, task_id):
    if request.method != "POST":
        return redirect("task_detail", task_id=task_id)

    task = get_object_or_404(Task.objects.select_for_update(), id=task_id, status="active")
    existing = TaskClaim.objects.filter(task=task, worker=request.user).first()

    if existing:
        return redirect("task_marketplace")

    if task.completed_workers >= task.max_workers:
        return redirect("task_marketplace")

    TaskClaim.objects.create(task=task, worker=request.user)
    task.completed_workers += 1
    if task.completed_workers >= task.max_workers:
        task.status = "completed"
    task.save(update_fields=["completed_workers", "status"])

    return redirect("task_marketplace")


@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    claim = TaskClaim.objects.filter(task=task, worker=request.user).first()

    return render(request, "tasks/task_detail.html", {"task": task, "claim": claim})


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

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Submit Task</title>
        <style>
            body {{ font-family: Arial; background: #f4f7fb; padding: 20px; }}
            .box {{ max-width: 600px; margin: auto; background: white; padding: 25px; border-radius: 20px; box-shadow: 0 5px 20px #0001; }}
            textarea {{ width: 100%; min-height: 160px; padding: 12px; border: 1px solid #ddd; border-radius: 12px; margin: 12px 0; }}
            button {{ width: 100%; padding: 14px; border: 0; border-radius: 12px; background: #2563eb; color: white; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="box">
            <h1>Submit Task</h1>
            <h2>{claim.task.title}</h2>
            <p>{claim.task.description}</p>
            <form method="post">
                <input type="hidden" name="csrfmiddlewaretoken" value="{request.META.get('CSRF_COOKIE', '')}">
                <textarea name="proof" placeholder="Write your completion details..." required></textarea>
                <button type="submit">Submit for Review</button>
            </form>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)
PY

# Migrations
python manage.py makemigrations wallet && \
python manage.py migrate && \
python manage.py check && \
echo "✅ Complete setup finished" && \
python manage.py runserver 0.0.0.0:8000

