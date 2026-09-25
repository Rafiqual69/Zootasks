from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import redirect, render

from .forms import RegistrationForm
from .models import WorkerProfile
from wallet.models import WalletTransaction


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            WorkerProfile.objects.create(user=user)
            login(request, user)
            return redirect("dashboard")
    else:
        form = RegistrationForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form},
    )


@login_required
def dashboard(request):
    profile, _ = WorkerProfile.objects.get_or_create(
        user=request.user
    )

    transactions = WalletTransaction.objects.filter(
        user=request.user
    ).order_by("-created_at")[:10]

    total_earned = (
        WalletTransaction.objects.filter(
            user=request.user,
            transaction_type="earning",
        ).aggregate(total=Sum("amount"))["total"]
        or 0
    )

    total_withdrawn = (
        WalletTransaction.objects.filter(
            user=request.user,
            transaction_type="withdrawal",
        ).aggregate(total=Sum("amount"))["total"]
        or 0
    )

    balance = profile.balance

    completed_tasks = (
        WalletTransaction.objects.filter(
            user=request.user,
            transaction_type="earning",
        ).count()
    )

    return render(
        request,
        "accounts/dashboard.html",
        {
            "profile": profile,
            "transactions": transactions,
            "balance": balance,
            "total_earned": total_earned,
            "total_withdrawn": total_withdrawn,
            "completed_tasks": completed_tasks,
        },
    )
