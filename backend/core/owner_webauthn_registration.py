"""Owner WebAuthn registration service; no endpoint/UI is enabled by this module alone."""
from __future__ import annotations

from datetime import datetime, timedelta
import hashlib
import hmac
from urllib.parse import urlsplit
from uuid import uuid4

from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone
from webauthn import generate_registration_options, options_to_json, verify_registration_response
from webauthn.helpers import base64url_to_bytes, bytes_to_base64url
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    PublicKeyCredentialDescriptor,
    UserVerificationRequirement,
)

from .models import OwnerWebAuthnChallenge, OwnerWebAuthnCredential


CHALLENGE_TTL = timedelta(minutes=5)


class OwnerWebAuthnRegistrationDenied(PermissionError):
    """Raised when a WebAuthn registration cannot be completed safely."""


def _validate_rp_configuration(*, rp_id: str, origin: str, rp_name: str) -> None:
    if not all(isinstance(value, str) and value.strip() for value in (rp_id, origin, rp_name)):
        raise OwnerWebAuthnRegistrationDenied("Owner device enrollment denied.")
    if len(rp_id) > 253 or len(rp_name) > 128 or len(origin) > 512:
        raise OwnerWebAuthnRegistrationDenied("Owner device enrollment denied.")
    if rp_id != rp_id.lower() or any(ch.isspace() for ch in rp_id) or "/" in rp_id or ":" in rp_id:
        raise OwnerWebAuthnRegistrationDenied("Owner device enrollment denied.")
    try:
        parsed = urlsplit(origin)
        hostname = parsed.hostname
        _ = parsed.port  # Reject malformed ports.
    except ValueError as exc:
        raise OwnerWebAuthnRegistrationDenied("Owner device enrollment denied.") from exc
    if (
        parsed.scheme != "https"
        or not hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path
        or parsed.query
        or parsed.fragment
        or not (hostname == rp_id or hostname.endswith("." + rp_id))
    ):
        raise OwnerWebAuthnRegistrationDenied("Owner device enrollment denied.")


def create_owner_registration_options(
    *,
    owner_id: int,
    rp_id: str,
    rp_name: str,
    origin: str,
    now: datetime | None = None,
) -> tuple[str, str]:
    """Create expiring registration options and persist the one-time challenge.

    Returns (challenge_record_id, options_json). The caller must separately
    authenticate/re-authorize the Owner before invoking this service.
    """
    if not isinstance(owner_id, int) or isinstance(owner_id, bool) or owner_id <= 0:
        raise OwnerWebAuthnRegistrationDenied("Owner device enrollment denied.")
    _validate_rp_configuration(rp_id=rp_id, origin=origin, rp_name=rp_name)
    current_time = now or timezone.now()

    active_credentials = OwnerWebAuthnCredential.objects.filter(
        owner_id=owner_id,
        revoked_at__isnull=True,
    ).only("credential_id")
    exclude_credentials = []
    try:
        for item in active_credentials:
            exclude_credentials.append(
                PublicKeyCredentialDescriptor(
                    id=base64url_to_bytes(item.credential_id),
                )
            )
        options = generate_registration_options(
            rp_id=rp_id,
            rp_name=rp_name,
            # Stable opaque user handle: do not expose sequential database IDs.
            user_id=hmac.new(
                settings.SECRET_KEY.encode("utf-8"),
                f"zootasks-owner-webauthn:{owner_id}".encode("utf-8"),
                hashlib.sha256,
            ).digest(),
            user_name="zootasks-owner",
            user_display_name="ZooTasks Owner",
            authenticator_selection=AuthenticatorSelectionCriteria(
                user_verification=UserVerificationRequirement.REQUIRED,
            ),
            exclude_credentials=exclude_credentials,
        )
        options_json = options_to_json(options)
    except Exception as exc:
        raise OwnerWebAuthnRegistrationDenied("Owner device enrollment denied.") from exc

    # Invalidate older outstanding registration ceremonies for this Owner.
    with transaction.atomic():
        OwnerWebAuthnChallenge.objects.filter(
            owner_id=owner_id,
            ceremony=OwnerWebAuthnChallenge.Ceremony.REGISTRATION,
            consumed_at__isnull=True,
        ).update(consumed_at=current_time)
        challenge = OwnerWebAuthnChallenge.objects.create(
            owner_id=owner_id,
            challenge=options.challenge,
            ceremony=OwnerWebAuthnChallenge.Ceremony.REGISTRATION,
            expires_at=current_time + CHALLENGE_TTL,
        )
    return str(challenge.pk), options_json


def complete_owner_registration(
    *,
    owner_id: int,
    challenge_record_id: str,
    credential: dict,
    rp_id: str,
    rp_name: str,
    origin: str,
    now: datetime | None = None,
) -> OwnerWebAuthnCredential:
    """Consume a challenge once, verify registration, then persist public metadata.

    A failed attempt still consumes the challenge. Device IDs are generated by
    the server; the client cannot choose an identity or supply a public key.
    """
    if not isinstance(owner_id, int) or isinstance(owner_id, bool) or owner_id <= 0:
        raise OwnerWebAuthnRegistrationDenied("Owner device enrollment denied.")
    if (
        not isinstance(challenge_record_id, str)
        or not challenge_record_id.isascii()
        or not challenge_record_id.isdecimal()
        or len(challenge_record_id) > 20
        or int(challenge_record_id) <= 0
        or str(int(challenge_record_id)) != challenge_record_id
    ):
        raise OwnerWebAuthnRegistrationDenied("Owner device enrollment denied.")
    if not isinstance(credential, dict):
        raise OwnerWebAuthnRegistrationDenied("Owner device enrollment denied.")
    _validate_rp_configuration(rp_id=rp_id, origin=origin, rp_name=rp_name)
    current_time = now or timezone.now()

    with transaction.atomic():
        challenge_row = (
            OwnerWebAuthnChallenge.objects.select_for_update()
            .filter(
                pk=int(challenge_record_id),
                owner_id=owner_id,
                ceremony=OwnerWebAuthnChallenge.Ceremony.REGISTRATION,
                consumed_at__isnull=True,
                expires_at__gt=current_time,
            )
            .first()
        )
        if challenge_row is None:
            raise OwnerWebAuthnRegistrationDenied("Owner device enrollment denied.")
        challenge_bytes = bytes(challenge_row.challenge)
        challenge_row.consumed_at = current_time
        challenge_row.save(update_fields=("consumed_at",))

    try:
        verified = verify_registration_response(
            credential=credential,
            expected_challenge=challenge_bytes,
            expected_rp_id=rp_id,
            expected_origin=origin,
            require_user_verification=True,
        )
        if not verified.credential_id or not verified.credential_public_key:
            raise OwnerWebAuthnRegistrationDenied("Owner device enrollment denied.")
        credential_id = bytes_to_base64url(verified.credential_id)
        public_key = bytes(verified.credential_public_key)
        sign_count = int(verified.sign_count)
        if (
            not credential_id
            or len(credential_id) > 255
            or not public_key
            or len(public_key) > 4096
            or sign_count < 0
        ):
            raise OwnerWebAuthnRegistrationDenied("Owner device enrollment denied.")
    except OwnerWebAuthnRegistrationDenied:
        raise
    except Exception as exc:
        raise OwnerWebAuthnRegistrationDenied("Owner device enrollment denied.") from exc

    try:
        with transaction.atomic():
            return OwnerWebAuthnCredential.objects.create(
                owner_id=owner_id,
                device_id=uuid4().hex,
                credential_id=credential_id,
                public_key=public_key,
                sign_count=sign_count,
            )
    except IntegrityError as exc:
        # A credential ID is globally unique, including revoked credentials.
        raise OwnerWebAuthnRegistrationDenied("Owner device enrollment denied.") from exc
