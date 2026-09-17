from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F, Sum
from django.shortcuts import redirect, render

from .models import WalletTransaction, WithdrawalRequest
from accounts.models import WorkerProfile


MIN_WITHDRAWAL = Decimal("50.00")


def get_wallet_summary(user):
    total_earned = (
        WalletTransaction.objects
        .filter(
            user=user,
            transaction_type="earning",
        )
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    total_withdrawn = (
        WalletTransaction.objects
        .filter(
            user=user,
            transaction_type="withdrawal",
        )
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    profile = WorkerProfile.objects.get_or_create(
        user=user
    )[0]

    pending_withdrawals = profile.reserved_balance

    available_balance = profile.balance - profile.reserved_balance

    return {
        "total_earned": total_earned,
        "total_withdrawn": total_withdrawn,
        "pending_withdrawals": pending_withdrawals,
        "available_balance": available_balance,
    }


@login_required
def wallet(request):
    summary = get_wallet_summary(request.user)

    transactions = (
        WalletTransaction.objects
        .filter(user=request.user)
        .order_by("-created_at")[:20]
    )

    withdrawals = (
        WithdrawalRequest.objects
        .filter(user=request.user)
        .order_by("-requested_at")[:10]
    )

    return render(
        request,
        "wallet/wallet.html",
        {
            **summary,
            "transactions": transactions,
            "withdrawals": withdrawals,
            "minimum_withdrawal": MIN_WITHDRAWAL,
        },
    )


@login_required
@transaction.atomic
def request_withdrawal(request):
    summary = get_wallet_summary(request.user)
    error = ""

    if request.method == "POST":
        amount_text = request.POST.get("amount", "").strip()
        bank_name = request.POST.get("bank_name", "").strip()
        account_holder = request.POST.get("account_holder", "").strip()
        bank_account = request.POST.get("bank_account", "").strip()

        try:
            amount = Decimal(amount_text)
        except (InvalidOperation, TypeError):
            amount = Decimal("0.00")

        if amount < MIN_WITHDRAWAL:
            error = (
                f"Minimum withdrawal is "
                f"৳{MIN_WITHDRAWAL:.2f}."
            )

        elif amount > summary["available_balance"]:
            error = "Insufficient available balance."

        elif not bank_name or not account_holder or not bank_account:
            error = "Please complete all payment information."

        else:
            reserved = (
                WorkerProfile.objects
                .filter(
                    user=request.user,
                    balance__gte=F("reserved_balance") + amount,
                )
                .update(
                    reserved_balance=F("reserved_balance") + amount
                )
            )

            if not reserved:
                error = "Insufficient available balance."
            else:
                WithdrawalRequest.objects.create(
                user=request.user,
                amount=amount,
                bank_name=bank_name,
                account_holder=account_holder,
                bank_account=bank_account,
            )

            return redirect("withdrawal_success")

    return render(
        request,
        "wallet/withdrawal.html",
        {
            **summary,
            "minimum_withdrawal": MIN_WITHDRAWAL,
            "error": error,
        },
    )


@login_required
def withdrawal_success(request):
    summary = get_wallet_summary(request.user)

    return render(
        request,
        "wallet/withdrawal_success.html",
        {
            **summary,
        },
    )


@login_required
def withdrawal_history(request):
    withdrawals = (
        WithdrawalRequest.objects
        .filter(user=request.user)
        .order_by("-requested_at")
    )

    return render(
        request,
        "wallet/withdrawal_history.html",
        {
            "withdrawals": withdrawals,
        },
    )
