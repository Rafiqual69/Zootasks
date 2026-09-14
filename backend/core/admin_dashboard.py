from decimal import Decimal

from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Sum
from django.shortcuts import render

from accounts.models import WorkerProfile
from wallet.models import WalletTransaction, WithdrawalRequest


def live_wallet_dashboard(request):
    total_earned = (
        WalletTransaction.objects
        .filter(transaction_type="earning")
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    total_withdrawn = (
        WalletTransaction.objects
        .filter(transaction_type="withdrawal")
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    pending_withdrawals = (
        WithdrawalRequest.objects
        .filter(status="pending")
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    approved_withdrawals = (
        WithdrawalRequest.objects
        .filter(status="approved")
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    paid_withdrawals = (
        WithdrawalRequest.objects
        .filter(status="paid")
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    worker_balance = (
        WorkerProfile.objects
        .aggregate(total=Sum("balance"))["total"]
        or Decimal("0.00")
    )

    total_workers = User.objects.filter(
        is_staff=False,
        is_superuser=False,
    ).count()

    context = {
        **admin.site.each_context(request),

        "title": "Live Wallet Dashboard",

        "total_earned": total_earned,
        "total_withdrawn": total_withdrawn,
        "pending_withdrawals": pending_withdrawals,
        "approved_withdrawals": approved_withdrawals,
        "paid_withdrawals": paid_withdrawals,
        "worker_balance": worker_balance,
        "total_workers": total_workers,
    }

    return render(
        request,
        "admin/live_wallet_dashboard.html",
        context,
    )
