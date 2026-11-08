import hmac
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.contrib.auth.views import LoginView
from django.db import IntegrityError, transaction
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from .authorization import worker_required
from core.security_policy_engine import require_authorized
from .forms import (
    OwnerOTPAuthenticationForm,
    RegistrationForm,
    WhatsAppOTPVerifyForm,
    WhatsAppPhoneForm,
)
from .models import (
    AccountEntity,
    WhatsAppIdentity,
    WhatsAppOTPChallenge,
    WorkerProfile,
)
from .whatsapp import (
    WhatsAppDeliveryError,
    keyed_digest,
    otp_digest,
    send_whatsapp_otp,
)
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

# =============== WHATSAPP OTP AUTHENTICATION ===============
def _whatsapp_login_page(request, phone_form=None, verify_form=None, error=None):
    challenge_id = request.session.get("whatsapp_otp_challenge_id")
    return render(
        request,
        "accounts/whatsapp_login.html",
        {
            "phone_form": phone_form or WhatsAppPhoneForm(),
            "verify_form": verify_form or WhatsAppOTPVerifyForm(),
            "challenge_sent": bool(challenge_id),
            "whatsapp_otp_enabled": settings.WHATSAPP_OTP_ENABLED,
            "error": error,
        },
    )


def whatsapp_login(request):
    """Send and verify short-lived WhatsApp OTPs; no email/phone enumeration."""
    if request.method == "GET":
        return _whatsapp_login_page(request)

    if request.method != "POST":
        return _whatsapp_login_page(request, error="Unsupported request.")

    if not settings.WHATSAPP_OTP_ENABLED:
        return _whatsapp_login_page(
            request,
            error="WhatsApp sign-in is not configured yet.",
        )

    action = request.POST.get("action", "")
    now = timezone.now()
    # OTP challenge records contain temporary phone data only; purge after 24h.
    WhatsAppOTPChallenge.objects.filter(
        created_at__lt=now - timedelta(days=1)
    ).delete()

    if action == "send_otp":
        form = WhatsAppPhoneForm(request.POST)
        if not form.is_valid():
            return _whatsapp_login_page(request, phone_form=form)

        phone_number = form.cleaned_data["phone_number"]
        phone_hash = keyed_digest("phone:" + phone_number)
        remote_ip = request.META.get("REMOTE_ADDR", "unknown")
        requester_hash = keyed_digest("ip:" + remote_ip)
        hour_ago = now - timedelta(hours=1)

        recent_phone = WhatsAppOTPChallenge.objects.filter(
            phone_hash=phone_hash,
            created_at__gte=hour_ago,
        )
        recent_ip = WhatsAppOTPChallenge.objects.filter(
            requester_hash=requester_hash,
            created_at__gte=hour_ago,
        )
        latest = recent_phone.order_by("-created_at").first()

        if (
            recent_phone.count() >= settings.WHATSAPP_OTP_MAX_SENDS_PER_PHONE_HOUR
            or recent_ip.count() >= settings.WHATSAPP_OTP_MAX_SENDS_PER_IP_HOUR
            or (
                latest
                and latest.created_at
                > now - timedelta(seconds=settings.WHATSAPP_OTP_RESEND_SECONDS)
            )
        ):
            return _whatsapp_login_page(
                request,
                error="A code cannot be sent right now. Please wait and try again.",
            )

        code = f"{secrets.randbelow(900000) + 100000:06d}"
        try:
            with transaction.atomic():
                # Retire any previous pending code before issuing a fresh one.
                WhatsAppOTPChallenge.objects.filter(
                    phone_hash=phone_hash,
                    consumed_at__isnull=True,
                ).update(consumed_at=now, phone_number="")
                challenge = WhatsAppOTPChallenge.objects.create(
                    phone_number=phone_number,
                    phone_hash=phone_hash,
                    code_hash="pending",
                    requester_hash=requester_hash,
                    expires_at=now + timedelta(seconds=settings.WHATSAPP_OTP_TTL_SECONDS),
                )
                challenge.code_hash = otp_digest(challenge.pk, code)
                challenge.save(update_fields=["code_hash"])
        except IntegrityError:
            return _whatsapp_login_page(
                request,
                error="A code request is already being processed. Please try again shortly.",
            )

        try:
            send_whatsapp_otp(phone_number, code)
        except WhatsAppDeliveryError:
            challenge.consumed_at = now
            challenge.phone_number = ""
            challenge.save(update_fields=["consumed_at", "phone_number"])
            return _whatsapp_login_page(
                request,
                error="We could not send a code. Please try again later.",
            )

        request.session["whatsapp_otp_challenge_id"] = str(challenge.pk)
        request.session.modified = True
        return redirect("whatsapp_login")

    if action == "verify_otp":
        form = WhatsAppOTPVerifyForm(request.POST)
        challenge_id = request.session.get("whatsapp_otp_challenge_id")
        if not form.is_valid() or not challenge_id:
            return _whatsapp_login_page(
                request,
                verify_form=form,
                error="Enter the current six-digit code and try again.",
            )

        authenticated_user = None
        verification_error = None

        try:
            with transaction.atomic():
                challenge = (
                    WhatsAppOTPChallenge.objects.select_for_update()
                    .filter(pk=challenge_id)
                    .first()
                )
                if (
                    challenge is None
                    or challenge.consumed_at is not None
                    or challenge.expires_at <= now
                    or challenge.attempts >= settings.WHATSAPP_OTP_MAX_ATTEMPTS
                ):
                    if challenge is not None and challenge.consumed_at is None:
                        challenge.consumed_at = now
                        challenge.phone_number = ""
                        challenge.save(update_fields=["consumed_at", "phone_number"])
                    verification_error = "The code is invalid or expired. Request a new code."
                else:
                    challenge.attempts += 1
                    expected = otp_digest(challenge.pk, form.cleaned_data["code"])
                    valid = hmac.compare_digest(challenge.code_hash, expected)
                    if not valid:
                        if challenge.attempts >= settings.WHATSAPP_OTP_MAX_ATTEMPTS:
                            challenge.consumed_at = now
                            challenge.phone_number = ""
                        challenge.save(update_fields=["attempts", "consumed_at", "phone_number"])
                        verification_error = "The code is invalid or expired. Request a new code."
                    else:
                        challenge.consumed_at = now
                        challenge.save(update_fields=["attempts", "consumed_at"])
                        verified_phone = challenge.phone_number

                        identity = WhatsAppIdentity.objects.select_related("user").filter(
                            phone_number=verified_phone
                        ).first()

                        if request.user.is_authenticated:
                            candidate = request.user
                            entity = AccountEntity.objects.filter(user=candidate).first()
                            if (
                                candidate.is_staff
                                or candidate.is_superuser
                                or entity is None
                                or entity.entity_type != AccountEntity.EntityType.WORKER
                                or not entity.is_active
                            ):
                                verification_error = "This account cannot use WhatsApp sign-in."
                            elif identity and identity.user_id != candidate.pk:
                                verification_error = "This phone number is already linked to another account."
                            else:
                                if identity is None:
                                    WhatsAppIdentity.objects.create(
                                        user=candidate,
                                        phone_number=verified_phone,
                                        verified_at=now,
                                    )
                                authenticated_user = candidate
                        elif identity is not None:
                            candidate = identity.user
                            entity = AccountEntity.objects.filter(user=candidate).first()
                            if (
                                not candidate.is_active
                                or candidate.is_staff
                                or candidate.is_superuser
                                or entity is None
                                or entity.entity_type != AccountEntity.EntityType.WORKER
                                or not entity.is_active
                            ):
                                verification_error = "This account cannot use WhatsApp sign-in."
                            else:
                                authenticated_user = candidate
                        else:
                            username = "wa_" + challenge.phone_hash[:24]
                            if get_user_model().objects.filter(username=username).exists():
                                username = "wa_" + secrets.token_hex(16)
                            candidate = get_user_model().objects.create_user(
                                username=username,
                                password=None,
                            )
                            WorkerProfile.objects.get_or_create(user=candidate)
                            AccountEntity.objects.create(
                                user=candidate,
                                entity_type=AccountEntity.EntityType.WORKER,
                                is_active=True,
                            )
                            WhatsAppIdentity.objects.create(
                                user=candidate,
                                phone_number=verified_phone,
                                verified_at=now,
                            )
                            authenticated_user = candidate

                        challenge.phone_number = ""
                        challenge.save(update_fields=["phone_number"])
        except IntegrityError:
            verification_error = "The phone number could not be linked. Please sign in and try again."

        if verification_error or authenticated_user is None:
            request.session.pop("whatsapp_otp_challenge_id", None)
            request.session.modified = True
            return _whatsapp_login_page(
                request,
                error=verification_error or "Verification could not be completed.",
            )

        request.session.pop("whatsapp_otp_challenge_id", None)
        request.session.modified = True
        if not request.user.is_authenticated:
            login(
                request,
                authenticated_user,
                backend="django.contrib.auth.backends.ModelBackend",
            )
        return redirect("dashboard")

    return _whatsapp_login_page(request, error="Choose a valid sign-in action.")
