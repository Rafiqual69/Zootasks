from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.urls import reverse

from .authorization import worker_required
from core.security_policy_engine import require_authorized
from .forms import OwnerOTPAuthenticationForm, RegistrationForm
from .models import AccountEntity, WorkerProfile
from wallet.models import WalletTransaction


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                WorkerProfile.objects.create(user=user)
                AccountEntity.objects.create(
                    user=user,
                    entity_type=AccountEntity.EntityType.WORKER,
                )
            login(request, user)
            return redirect("dashboard")
    else:
        form = RegistrationForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form},
    )


@worker_required
def dashboard(request):
    require_authorized(
        actor="worker", resource="worker_profile", action="read", scope="own",
        facts={"account_entity.active_worker": True, "object.owner_is_actor": True},
    )
    require_authorized(
        actor="worker", resource="wallet", action="read", scope="own",
        facts={"account_entity.active_worker": True, "object.owner_is_actor": True},
    )
    require_authorized(
        actor="worker", resource="wallet_transaction", action="read", scope="own",
        facts={"account_entity.active_worker": True, "object.owner_is_actor": True},
    )
    profile = WorkerProfile.objects.get(user=request.user)

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


class OwnerLoginView(LoginView):
    """High-assurance Owner login with a privileged landing boundary."""

    template_name = "accounts/owner_login.html"
    authentication_form = OwnerOTPAuthenticationForm
    redirect_authenticated_user = False

    def get_success_url(self):
        return reverse("admin:index")

    def form_valid(self, form):
        response = super().form_valid(form)
        from django.utils import timezone

        self.request.session["owner_reauthenticated_at"] = timezone.now().isoformat()
        self.request.session.modified = True
        return response
