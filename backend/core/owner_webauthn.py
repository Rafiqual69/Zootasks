"""Server-side WebAuthn verification boundary for Owner approvals."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from django.db import transaction
from django.utils import timezone
from webauthn import verify_authentication_response
from webauthn.helpers import base64url_to_bytes

from .models import OwnerWebAuthnCredential


class OwnerWebAuthnDenied(PermissionError):
    """Raised when an Owner WebAuthn assertion cannot be trusted."""


@dataclass(frozen=True)
class VerifiedOwnerWebAuthn:
    owner_id: int
    device_id: str
    credential_id: str
    sign_count: int
    user_verified: bool


@transaction.atomic
def verify_owner_webauthn_assertion(
    *,
    owner_id: int,
    credential_id: str,
    credential: Any,
    expected_challenge: bytes,
    expected_rp_id: str,
    expected_origin: str,
    now: datetime | None = None,
) -> VerifiedOwnerWebAuthn:
    """Verify one Owner assertion and atomically advance its sign counter."""
    if not isinstance(credential_id, str) or not credential_id:
        raise OwnerWebAuthnDenied("Owner authentication denied.")
    if not isinstance(expected_rp_id, str) or not expected_rp_id:
        raise OwnerWebAuthnDenied("Owner authentication denied.")
    if not isinstance(expected_origin, str) or not expected_origin:
        raise OwnerWebAuthnDenied("Owner authentication denied.")
    if not isinstance(expected_challenge, bytes) or not expected_challenge:
        raise OwnerWebAuthnDenied("Owner authentication denied.")

    try:
        credential_id_bytes = base64url_to_bytes(credential_id)
    except Exception as exc:
        raise OwnerWebAuthnDenied("Owner authentication denied.") from exc

    stored = (
        OwnerWebAuthnCredential.objects.select_for_update()
        .filter(
            owner_id=owner_id,
            credential_id=credential_id,
            revoked_at__isnull=True,
        )
        .first()
    )
    if stored is None:
        raise OwnerWebAuthnDenied("Owner authentication denied.")

    try:
        verified = verify_authentication_response(
            credential=credential,
            expected_challenge=expected_challenge,
            expected_rp_id=expected_rp_id,
            expected_origin=expected_origin,
            credential_public_key=bytes(stored.public_key),
            credential_current_sign_count=stored.sign_count,
            require_user_verification=True,
        )
    except Exception as exc:
        raise OwnerWebAuthnDenied("Owner authentication denied.") from exc

    if verified.credential_id != credential_id_bytes or not verified.user_verified:
        raise OwnerWebAuthnDenied("Owner authentication denied.")
    if verified.new_sign_count < stored.sign_count:
        raise OwnerWebAuthnDenied("Owner authentication denied.")

    current_time = now or timezone.now()
    stored.sign_count = verified.new_sign_count
    stored.last_used_at = current_time
    stored.save(update_fields=("sign_count", "last_used_at"))

    return VerifiedOwnerWebAuthn(
        owner_id=owner_id,
        device_id=stored.device_id,
        credential_id=stored.credential_id,
        sign_count=stored.sign_count,
        user_verified=verified.user_verified,
    )
