"""Fail-closed Owner WebAuthn authentication challenge lifecycle.

This service issues/consumes authentication challenges only. It does not create
sessions, authorize protected actions, or enable an HTTP endpoint.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from webauthn import generate_authentication_options, options_to_json
from webauthn.helpers import base64url_to_bytes
from webauthn.helpers.structs import (
    PublicKeyCredentialDescriptor,
    UserVerificationRequirement,
)

from .models import OwnerWebAuthnChallenge, OwnerWebAuthnCredential
from .owner_webauthn_registration import (
    OwnerWebAuthnRegistrationDenied,
    _require_configured_owner,
    _validate_rp_configuration,
)

AUTHENTICATION_CHALLENGE_TTL = timedelta(minutes=5)


class OwnerWebAuthnChallengeDenied(PermissionError):
    """Raised when an authentication challenge cannot be issued or consumed."""


@dataclass(frozen=True)
class ConsumedOwnerAuthenticationChallenge:
    owner_id: int
    challenge: bytes
    rp_id: str
    origin: str


def _configured_rp() -> tuple[str, str]:
    rp_id = getattr(settings, "OWNER_WEBAUTHN_RP_ID", "")
    origin = getattr(settings, "OWNER_WEBAUTHN_ORIGIN", "")
    try:
        _validate_rp_configuration(rp_id=rp_id, origin=origin, rp_name="ZooTasks")
    except OwnerWebAuthnRegistrationDenied as exc:
        raise OwnerWebAuthnChallengeDenied(
            "Owner authentication challenge denied."
        ) from exc
    return rp_id, origin


def create_owner_authentication_options(
    *,
    owner_id: int,
    now: datetime | None = None,
) -> tuple[str, str]:
    """Issue a short-lived challenge bound to configured Owner/RP/origin.

    Caller authorization and rate limiting are separate mandatory route duties.
    No route is enabled by this helper alone.
    """
    try:
        _require_configured_owner(owner_id)
    except OwnerWebAuthnRegistrationDenied as exc:
        raise OwnerWebAuthnChallengeDenied(
            "Owner authentication challenge denied."
        ) from exc

    rp_id, origin = _configured_rp()
    current_time = now or timezone.now()
    credentials = list(
        OwnerWebAuthnCredential.objects.filter(
            owner_id=owner_id,
            revoked_at__isnull=True,
        ).only("credential_id")
    )
    if not credentials:
        raise OwnerWebAuthnChallengeDenied("Owner authentication challenge denied.")

    try:
        allow_credentials = [
            PublicKeyCredentialDescriptor(id=base64url_to_bytes(item.credential_id))
            for item in credentials
        ]
        options = generate_authentication_options(
            rp_id=rp_id,
            allow_credentials=allow_credentials,
            user_verification=UserVerificationRequirement.REQUIRED,
            timeout=int(AUTHENTICATION_CHALLENGE_TTL.total_seconds() * 1000),
        )
        options_json = options_to_json(options)
    except Exception as exc:
        raise OwnerWebAuthnChallengeDenied(
            "Owner authentication challenge denied."
        ) from exc

    with transaction.atomic():
        owner_row = get_user_model().objects.select_for_update().filter(pk=owner_id).first()
        if owner_row is None:
            raise OwnerWebAuthnChallengeDenied("Owner authentication challenge denied.")
        OwnerWebAuthnChallenge.objects.filter(
            owner_id=owner_id,
            ceremony=OwnerWebAuthnChallenge.Ceremony.AUTHENTICATION,
            consumed_at__isnull=True,
        ).update(consumed_at=current_time)
        challenge = OwnerWebAuthnChallenge.objects.create(
            owner_id=owner_id,
            challenge=options.challenge,
            rp_id=rp_id,
            origin=origin,
            ceremony=OwnerWebAuthnChallenge.Ceremony.AUTHENTICATION,
            expires_at=current_time + AUTHENTICATION_CHALLENGE_TTL,
        )
    return str(challenge.pk), options_json


def consume_owner_authentication_challenge(
    *,
    owner_id: int,
    challenge_record_id: str,
    now: datetime | None = None,
) -> ConsumedOwnerAuthenticationChallenge:
    """Consume one current, unexpired challenge and return its trusted context.

    The caller must pass the returned challenge/RP/origin to the assertion
    verifier. Consumption commits before configuration mismatch is rejected,
    so a failed ceremony cannot replay the same challenge.
    """
    try:
        _require_configured_owner(owner_id)
    except OwnerWebAuthnRegistrationDenied as exc:
        raise OwnerWebAuthnChallengeDenied(
            "Owner authentication challenge denied."
        ) from exc

    if (
        not isinstance(challenge_record_id, str)
        or not challenge_record_id.isascii()
        or not challenge_record_id.isdecimal()
        or len(challenge_record_id) > 20
        or int(challenge_record_id) <= 0
        or str(int(challenge_record_id)) != challenge_record_id
    ):
        raise OwnerWebAuthnChallengeDenied("Owner authentication challenge denied.")

    current_time = now or timezone.now()
    with transaction.atomic():
        row = (
            OwnerWebAuthnChallenge.objects.select_for_update()
            .filter(
                pk=int(challenge_record_id),
                owner_id=owner_id,
                ceremony=OwnerWebAuthnChallenge.Ceremony.AUTHENTICATION,
                consumed_at__isnull=True,
                expires_at__gt=current_time,
            )
            .first()
        )
        if row is None:
            raise OwnerWebAuthnChallengeDenied("Owner authentication challenge denied.")
        challenge_bytes = bytes(row.challenge)
        stored_rp_id = row.rp_id
        stored_origin = row.origin
        row.consumed_at = current_time
        row.save(update_fields=("consumed_at",))

    rp_id, origin = _configured_rp()
    if stored_rp_id != rp_id or stored_origin != origin:
        raise OwnerWebAuthnChallengeDenied("Owner authentication challenge denied.")

    return ConsumedOwnerAuthenticationChallenge(
        owner_id=owner_id,
        challenge=challenge_bytes,
        rp_id=rp_id,
        origin=origin,
    )
