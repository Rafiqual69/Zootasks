from datetime import timedelta
from decimal import Decimal

from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Q, Sum
from django.shortcuts import render
from django.utils import timezone

from accounts.models import AccountEntity, WorkerProfile
from core.security_policy_engine import require_authorized
from wallet.models import WalletTransaction, WithdrawalRequest


OWNER_REAUTH_MAX_AGE = timedelta(minutes=15)


def _owner_dashboard_facts(request):
    """Build privileged-dashboard facts only from trusted server-side state."""
    if not request.user.is_authenticated:
        return {}

    try:
        entity = AccountEntity.objects.get(user=request.user)
    except AccountEntity.DoesNotExist:
        return {}

    reauth_raw = request.session.get("owner_reauthenticated_at")
    reauth_fresh = False
    if reauth_raw:
        try:
            reauth_at = timezone.datetime.fromisoformat(reauth_raw)
            if timezone.is_naive(reauth_at):
                reauth_at = timezone.make_aware(
                    reauth_at, timezone.get_current_timezone()
                )
            reauth_fresh = timezone.now() - reauth_at <= OWNER_REAUTH_MAX_AGE
        except (TypeError, ValueError):
            reauth_fresh = False

    return {
        "owner_authenticated": request.user.is_authenticated,
        "privileged_reauth_required": reauth_fresh,
        "canonical_owner_boundary": (
            entity.is_active
            and entity.entity_type == AccountEntity.EntityType.OWNER
            and User.objects.filter(
                pk=request.user.pk, is_staff=True, is_superuser=True
            ).exists()
        ),
    }


def live_wallet_dashboard(request):
    require_authorized(
        actor="owner",
        resource="admin_wallet_dashboard",
        action="read",
        scope="global",
        facts=_owner_dashboard_facts(request),
    )

    wallet_totals = WalletTransaction.objects.aggregate(
        total_earned=Sum("amount", filter=Q(transaction_type="earning")),
        total_withdrawn=Sum("amount", filter=Q(transaction_type="withdrawal")),
    )

    total_earned = wallet_totals["total_earned"] or Decimal("0.00")
    total_withdrawn = wallet_totals["total_withdrawn"] or Decimal("0.00")

    withdrawal_totals = WithdrawalRequest.objects.aggregate(
        pending_withdrawals=Sum("amount", filter=Q(status="pending")),
        approved_withdrawals=Sum("amount", filter=Q(status="approved")),
        paid_withdrawals=Sum("amount", filter=Q(status="paid")),
    )

    pending_withdrawals = withdrawal_totals["pending_withdrawals"] or Decimal("0.00")
    approved_withdrawals = withdrawal_totals["approved_withdrawals"] or Decimal("0.00")
    paid_withdrawals = withdrawal_totals["paid_withdrawals"] or Decimal("0.00")

    worker_balance = (
        WorkerProfile.objects.aggregate(total=Sum("balance"))["total"]
        or Decimal("0.00")
    )

    total_workers = User.objects.filter(is_staff=False, is_superuser=False).count()

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

    return render(request, "admin/live_wallet_dashboard.html", context)
