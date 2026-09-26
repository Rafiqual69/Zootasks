import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from .models import AccountEntity, OwnerEmailVerificationChallenge


TOKEN_TTL = timedelta(minutes=15)
MAX_ATTEMPTS = 5


def _hash_token(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


@transaction.atomic
def issue_owner_email_verification(request, user):
    entity = AccountEntity.objects.select_for_update().get(
        user=user,
        entity_type=AccountEntity.EntityType.OWNER,
        is_active=True,
    )
    if not entity.identity_email:
        raise ValueError("Owner identity email is not configured.")
    if entity.email_verified_at:
        raise ValueError("Owner identity email is already verified.")

    OwnerEmailVerificationChallenge.objects.filter(
        account_entity=entity,
        used_at__isnull=True,
    ).update(used_at=timezone.now())

    token = secrets.token_urlsafe(32)
    challenge = OwnerEmailVerificationChallenge.objects.create(
        account_entity=entity,
        token_hash=_hash_token(token),
        expires_at=timezone.now() + TOKEN_TTL,
    )
    verify_url = request.build_absolute_uri(
        reverse("owner_email_verify", kwargs={"token": token})
    )
    send_mail(
        subject="ZooTasks Owner email verification",
        message=(
            "Verify the Owner identity email for ZooTasks.\n\n"
            f"Verification link (expires in 15 minutes):\n{verify_url}\n\n"
            "If you did not request this, ignore this message."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[entity.identity_email],
        fail_silently=False,
    )
    return challenge


@transaction.atomic
def verify_owner_email_token(token):
    token_hash = _hash_token(token)
    challenge = (
        OwnerEmailVerificationChallenge.objects
        .select_for_update()
        .select_related("account_entity")
        .filter(token_hash=token_hash)
        .first()
    )
    if not challenge or not challenge.is_valid():
        return False

    challenge.attempts += 1
    challenge.used_at = timezone.now()
    challenge.save(update_fields=["attempts", "used_at"])

    entity = challenge.account_entity
    entity.email_verified_at = timezone.now()
    entity.save(update_fields=["email_verified_at", "updated_at"])
    return True
