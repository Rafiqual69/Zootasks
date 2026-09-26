from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .email_verification import issue_owner_email_verification, verify_owner_email_token
from .forms import AdvertiserRegistrationForm, RegistrationForm
from .models import AccountEntity, AdvertiserProfile, WorkerProfile
from .policies import is_owner
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
    return render(request, "accounts/register.html", {"form": form})


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
    return render(request, "accounts/register.html", {"form": form, "account_type": "advertiser"})


@login_required
@user_passes_test(is_owner)
def owner_email_verification_request(request):
    if request.method != "POST":
        return HttpResponse("Owner email verification requires POST.", status=405)
    issue_owner_email_verification(request, request.user)
    return HttpResponse("Owner email verification email sent.")


def owner_email_verify(request, token):
    if request.method == "GET":
        response = render(
            request,
            "accounts/owner_email_verify.html",
            {"token": token},
        )
        response["Referrer-Policy"] = "no-referrer"
        response["Cache-Control"] = "no-store"
        return response

    if request.method != "POST":
        return HttpResponse("Owner email verification requires GET or POST.", status=405)

    if verify_owner_email_token(token):
        response = HttpResponse("Owner identity email verified successfully.")
        response["Referrer-Policy"] = "no-referrer"
        response["Cache-Control"] = "no-store"
        return response

    response = HttpResponse(
        "Invalid, expired, already-used, or exhausted verification token.",
        status=400,
    )
    response["Referrer-Policy"] = "no-referrer"
    response["Cache-Control"] = "no-store"
    return response


@login_required
def dashboard(request):
    try:
        entity = request.user.account_entity
    except AccountEntity.DoesNotExist as exc:
        raise PermissionDenied("A Worker account entity is required for this dashboard.") from exc
    if not entity.is_active or entity.entity_type != AccountEntity.EntityType.WORKER:
        raise PermissionDenied("This dashboard is restricted to active Worker accounts.")
    try:
        profile = request.user.workerprofile
    except WorkerProfile.DoesNotExist as exc:
        raise PermissionDenied("Worker profile is not provisioned.") from exc
    transactions = WalletTransaction.objects.filter(user=request.user).order_by("-created_at")[:10]
    total_earned = WalletTransaction.objects.filter(
        user=request.user, transaction_type="earning"
    ).aggregate(total=Sum("amount"))["total"] or 0
    total_withdrawn = WalletTransaction.objects.filter(
        user=request.user, transaction_type="withdrawal"
    ).aggregate(total=Sum("amount"))["total"] or 0
    completed_tasks = WalletTransaction.objects.filter(
        user=request.user, transaction_type="earning"
    ).count()
    return render(request, "accounts/dashboard.html", {
        "profile": profile,
        "transactions": transactions,
        "balance": profile.balance,
        "total_earned": total_earned,
        "total_withdrawn": total_withdrawn,
        "completed_tasks": completed_tasks,
    })


@login_required
def advertiser_dashboard(request):
    try:
        entity = request.user.account_entity
    except AccountEntity.DoesNotExist as exc:
        raise PermissionDenied("An Advertiser account entity is required for this dashboard.") from exc
    if not entity.is_active or entity.entity_type != AccountEntity.EntityType.ADVERTISER:
        raise PermissionDenied("This dashboard is restricted to active Advertiser accounts.")
    try:
        profile = request.user.advertiser_profile
    except AdvertiserProfile.DoesNotExist as exc:
        raise PermissionDenied("Advertiser profile is not provisioned.") from exc
    promotions = Promotion.objects.filter(advertiser=profile).order_by("-created_at")
    return render(request, "accounts/advertiser_dashboard.html", {"profile": profile, "promotions": promotions})


from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.views.decorators.http import require_GET

from .models import OwnerSocialIdentity
from .policies import is_owner
from .social_oauth import consume_owner_social_oauth_state, issue_owner_social_oauth_state
from .social_oauth_provider import build_owner_social_authorization_url


def _no_store(response):
    response["Cache-Control"] = "no-store"
    response["Pragma"] = "no-cache"
    response["Referrer-Policy"] = "no-referrer"
    return response


@login_required
@require_GET
def owner_social_oauth_start(request, provider):
    if not is_owner(request.user):
        return _no_store(HttpResponse(status=403))

    if provider not in OwnerSocialIdentity.Provider.values:
        return _no_store(HttpResponseBadRequest("Unsupported social provider."))

    try:
        state = issue_owner_social_oauth_state(request.user, provider)
        authorization_url = build_owner_social_authorization_url(provider, state)
    except (PermissionError, ValueError):
        return _no_store(HttpResponseBadRequest("Social OAuth is not configured."))

    return _no_store(HttpResponseRedirect(authorization_url))


@login_required
@require_GET
def owner_social_oauth_callback(request, provider):
    if not is_owner(request.user):
        return _no_store(HttpResponse(status=403))

    if provider not in OwnerSocialIdentity.Provider.values:
        return _no_store(HttpResponseBadRequest("Unsupported social provider."))

    if request.GET.get("error"):
        return _no_store(HttpResponseBadRequest("Social authorization was not completed."))

    code = request.GET.get("code", "")
    state = request.GET.get("state", "")
    if not code or not state:
        return _no_store(HttpResponseBadRequest("Missing OAuth callback parameters."))

    owner_entity = consume_owner_social_oauth_state(state, provider)
    if owner_entity is None or owner_entity.user_id != request.user.id:
        return _no_store(HttpResponseBadRequest("Invalid or expired OAuth state."))

    # Provider-specific authorization-code exchange and identity verification
    # are intentionally not implemented in this foundation step. No provider
    # access token is accepted or stored here.
    return _no_store(
        HttpResponse(
            "OAuth state verified. Provider identity exchange is not enabled yet.",
            status=501,
        )
    )
