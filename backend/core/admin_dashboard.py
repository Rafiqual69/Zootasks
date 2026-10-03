from decimal import Decimal

from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Q, Sum
from django.shortcuts import render

from accounts.models import WorkerProfile
from wallet.models import WalletTransaction, WithdrawalRequest


def live_wallet_dashboard(request):
    if not request.user.has_perm("wallet.view_live_wallet_dashboard"):
        from django.core.exceptions import PermissionDenied

        raise PermissionDenied

    wallet_totals = WalletTransaction.objects.aggregate(
        total_earned=Sum(
            "amount",
            filter=Q(transaction_type="earning"),
        ),
        total_withdrawn=Sum(
            "amount",
            filter=Q(transaction_type="withdrawal"),
        ),
    )

    total_earned = wallet_totals["total_earned"] or Decimal("0.00")
    total_withdrawn = wallet_totals["total_withdrawn"] or Decimal("0.00")

    withdrawal_totals = WithdrawalRequest.objects.aggregate(
        pending_withdrawals=Sum(
            "amount",
            filter=Q(status="pending"),
        ),
        approved_withdrawals=Sum(
            "amount",
            filter=Q(status="approved"),
        ),
        paid_withdrawals=Sum(
            "amount",
            filter=Q(status="paid"),
        ),
    )

    pending_withdrawals = (
        withdrawal_totals["pending_withdrawals"] or Decimal("0.00")
    )
    approved_withdrawals = (
        withdrawal_totals["approved_withdrawals"] or Decimal("0.00")
    )
    paid_withdrawals = (
        withdrawal_totals["paid_withdrawals"] or Decimal("0.00")
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
