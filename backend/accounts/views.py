from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AdvertiserRegistrationForm, RegistrationForm
from .models import AccountEntity, AdvertiserProfile, WorkerProfile
from promotions.models import Promotion
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
                    identity_email=user.email or None,
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


def advertiser_register(request):
    if request.user.is_authenticated:
        try:
            entity_type = request.user.account_entity.entity_type
        except AccountEntity.DoesNotExist:
            raise PermissionDenied("Authenticated accounts cannot create a second account entity.")
        if entity_type == AccountEntity.EntityType.ADVERTISER:
            return redirect("advertiser_dashboard")
        return redirect("dashboard")

    if request.method == "POST":
        form = AdvertiserRegistrationForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                AccountEntity.objects.create(
                    user=user,
                    entity_type=AccountEntity.EntityType.ADVERTISER,
                    identity_email=user.email or None,
                )
                AdvertiserProfile.objects.create(
                    user=user,
                    organization_name=form.cleaned_data["organization_name"],
                    contact_name=form.cleaned_data["contact_name"],
                )
            return redirect("login")
    else:
        form = AdvertiserRegistrationForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form, "account_type": "advertiser"},
    )


@login_required
def dashboard(request):
    try:
        entity = request.user.account_entity
    except AccountEntity.DoesNotExist as exc:
        raise PermissionDenied("A Worker account entity is required for this dashboard.") from exc

    if (
        not entity.is_active
        or entity.entity_type != AccountEntity.EntityType.WORKER
    ):
        raise PermissionDenied("This dashboard is restricted to active Worker accounts.")

    try:
        profile = request.user.workerprofile
    except WorkerProfile.DoesNotExist as exc:
        raise PermissionDenied("Worker profile is not provisioned.") from exc

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


@login_required
def advertiser_dashboard(request):
    try:
        entity = request.user.account_entity
    except AccountEntity.DoesNotExist as exc:
        raise PermissionDenied("An Advertiser account entity is required for this dashboard.") from exc

    if (
        not entity.is_active
        or entity.entity_type != AccountEntity.EntityType.ADVERTISER
    ):
        raise PermissionDenied("This dashboard is restricted to active Advertiser accounts.")

    try:
        profile = request.user.advertiser_profile
    except AdvertiserProfile.DoesNotExist as exc:
        raise PermissionDenied("Advertiser profile is not provisioned.") from exc

    promotions = Promotion.objects.filter(advertiser=profile).order_by("-created_at")

    return render(
        request,
        "accounts/advertiser_dashboard.html",
        {"profile": profile, "promotions": promotions},
    )
