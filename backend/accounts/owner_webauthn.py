import base64
import hashlib
import json
import secrets
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from webauthn import (
    generate_authentication_options,
    generate_registration_options,
    options_to_json,
    verify_authentication_response,
    verify_registration_response,
)
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    PublicKeyCredentialDescriptor,
    ResidentKeyRequirement,
    UserVerificationRequirement,
)

from .models import (
    AccountEntity,
    OwnerWebAuthnChallenge,
    OwnerWebAuthnCredential,
)
from .owner_session_binding import bind_owner_session_webauthn
from .policies import is_owner

CHALLENGE_BYTES = 32
MAX_ACTIVE_CREDENTIALS = 3


def _hash(value):
    return hashlib.sha256(value).hexdigest()


def _session_key_hash(request):
    session_key = request.session.session_key
    if not session_key:
        raise PermissionError("An active Owner session is required.")
    return _hash(session_key.encode("utf-8"))


def _owner_entity(owner_user):
    if not is_owner(owner_user):
        raise PermissionError("Canonical active Owner access is required.")
    return AccountEntity.objects.get(
        user=owner_user,
        entity_type=AccountEntity.EntityType.OWNER,
        is_active=True,
    )


def _require_recent_owner_reauth(request, owner_user):
    if request.user.pk != owner_user.pk:
        raise PermissionError("Owner session does not match the authenticated account.")
    timestamp = request.session.get("owner_reauthenticated_at")
    if not timestamp:
        raise PermissionError("Recent Owner re-authentication is required.")
    try:
        age = timezone.now().timestamp() - float(timestamp)
    except (TypeError, ValueError):
        raise PermissionError("Recent Owner re-authentication is required.")
    if age < 0 or age > settings.OWNER_WEBAUTHN_REAUTH_TTL_SECONDS:
        raise PermissionError("Recent Owner re-authentication is required.")


def _ensure_user_handle(entity):
    if entity.webauthn_user_handle:
        return entity.webauthn_user_handle
    entity.webauthn_user_handle = secrets.token_bytes(32)
    entity.save(update_fields=("webauthn_user_handle", "updated_at"))
    return entity.webauthn_user_handle


def _issue_challenge(request, entity, ceremony):
    session_hash = _session_key_hash(request)
    OwnerWebAuthnChallenge.objects.filter(
        owner_entity=entity,
        session_key_hash=session_hash,
        ceremony=ceremony,
        used_at__isnull=True,
    ).update(used_at=timezone.now())
    challenge = secrets.token_bytes(CHALLENGE_BYTES)
    record = OwnerWebAuthnChallenge.objects.create(
        owner_entity=entity,
        session_key_hash=session_hash,
        ceremony=ceremony,
        challenge_hash=_hash(challenge),
        expires_at=timezone.now()
        + timedelta(seconds=settings.OWNER_WEBAUTHN_CHALLENGE_TTL_SECONDS),
    )
    return record, challenge


def _consume_challenge(request, entity, ceremony, challenge):
    record = (
        OwnerWebAuthnChallenge.objects.select_for_update()
        .filter(
            owner_entity=entity,
            session_key_hash=_session_key_hash(request),
            ceremony=ceremony,
            challenge_hash=_hash(challenge),
            used_at__isnull=True,
        )
        .first()
    )
    if not record or not record.is_valid():
        raise ValidationError("Invalid or expired WebAuthn challenge.")
    record.used_at = timezone.now()
    record.save(update_fields=("used_at",))
    return record


@transaction.atomic
def issue_owner_webauthn_registration(request, owner_user):
    _require_recent_owner_reauth(request, owner_user)
    entity = AccountEntity.objects.select_for_update().get(
        pk=_owner_entity(owner_user).pk
    )
    active = OwnerWebAuthnCredential.objects.filter(
        owner_entity=entity,
        revoked_at__isnull=True,
    )
    if active.count() >= MAX_ACTIVE_CREDENTIALS:
        raise ValidationError("The Owner already has the maximum of 3 active passkeys.")

    _, challenge = _issue_challenge(
        request, entity, OwnerWebAuthnChallenge.Ceremony.REGISTRATION
    )
    request.session["owner_webauthn_registration_challenge"] = (
        base64.urlsafe_b64encode(challenge).decode("ascii")
    )
    options = generate_registration_options(
        rp_id=settings.OWNER_WEBAUTHN_RP_ID,
        rp_name="ZooTasks",
        user_id=_ensure_user_handle(entity),
        user_name=entity.user.username,
        user_display_name=entity.user.get_full_name() or entity.user.username,
        challenge=challenge,
        timeout=60000,
        authenticator_selection=AuthenticatorSelectionCriteria(
            resident_key=ResidentKeyRequirement.PREFERRED,
            user_verification=UserVerificationRequirement.REQUIRED,
        ),
        exclude_credentials=[
            PublicKeyCredentialDescriptor(id=credential.credential_id)
            for credential in active
        ],
    )
    return json.loads(options_to_json(options))


@transaction.atomic
def complete_owner_webauthn_registration(request, owner_user, credential, label=""):
    _require_recent_owner_reauth(request, owner_user)
    encoded = request.session.pop("owner_webauthn_registration_challenge", "")
    if not encoded:
        raise ValidationError("No active Owner WebAuthn registration challenge.")
    try:
        challenge = base64.urlsafe_b64decode(
            encoded + "=" * (-len(encoded) % 4)
        )
    except (ValueError, TypeError):
        raise ValidationError("Invalid Owner WebAuthn registration challenge.")
    credential_record = complete_owner_webauthn_registration_with_challenge(
        request, owner_user, credential, challenge
    )
    if label:
        credential_record.label = label[:100]
        credential_record.save(update_fields=("label",))
    return credential_record


@transaction.atomic
def complete_owner_webauthn_registration_with_challenge(
    request, owner_user, credential, challenge
):
    _require_recent_owner_reauth(request, owner_user)
    entity = AccountEntity.objects.select_for_update().get(
        pk=_owner_entity(owner_user).pk
    )
    _consume_challenge(
        request, entity, OwnerWebAuthnChallenge.Ceremony.REGISTRATION, challenge
    )
    verification = verify_registration_response(
        credential=credential,
        expected_challenge=challenge,
        expected_origin=settings.OWNER_WEBAUTHN_ORIGINS,
        expected_rp_id=settings.OWNER_WEBAUTHN_RP_ID,
        require_user_presence=True,
        require_user_verification=True,
    )
    if verification.credential_id in OwnerWebAuthnCredential.objects.values_list(
        "credential_id", flat=True
    ):
        raise ValidationError("This passkey is already registered.")
    if OwnerWebAuthnCredential.objects.filter(
        owner_entity=entity, revoked_at__isnull=True
    ).count() >= MAX_ACTIVE_CREDENTIALS:
        raise ValidationError("The Owner already has the maximum of 3 active passkeys.")
    credential_record = OwnerWebAuthnCredential.objects.create(
        owner_entity=entity,
        credential_id=verification.credential_id,
        public_key=verification.credential_public_key,
        user_handle=entity.webauthn_user_handle,
        sign_count=verification.sign_count,
        aaguid=verification.aaguid,
        backup_eligible=verification.credential_device_type.value == "multi_device",
        backed_up=verification.credential_backed_up,
        label="Owner passkey",
    )
    return credential_record


@transaction.atomic
def issue_owner_webauthn_authentication(request, owner_user):
    _require_recent_owner_reauth(request, owner_user)
    entity = AccountEntity.objects.get(
        pk=_owner_entity(owner_user).pk
    )
    credentials = OwnerWebAuthnCredential.objects.filter(
        owner_entity=entity,
        revoked_at__isnull=True,
    )
    if not credentials.exists():
        raise ValidationError("No active Owner passkey is enrolled.")
    _, challenge = _issue_challenge(
        request, entity, OwnerWebAuthnChallenge.Ceremony.AUTHENTICATION
    )
    request.session["owner_webauthn_authentication_challenge"] = (
        base64.urlsafe_b64encode(challenge).decode("ascii")
    )
    options = generate_authentication_options(
        rp_id=settings.OWNER_WEBAUTHN_RP_ID,
        challenge=challenge,
        timeout=60000,
        allow_credentials=[
            PublicKeyCredentialDescriptor(id=item.credential_id)
            for item in credentials
        ],
        user_verification=UserVerificationRequirement.REQUIRED,
    )
    return json.loads(options_to_json(options))


@transaction.atomic
def complete_owner_webauthn_authentication(request, owner_user, credential):
    _require_recent_owner_reauth(request, owner_user)
    entity = AccountEntity.objects.select_for_update().get(
        pk=_owner_entity(owner_user).pk
    )
    encoded = request.session.pop("owner_webauthn_authentication_challenge", "")
    if not encoded:
        raise ValidationError("No active Owner WebAuthn authentication challenge.")
    try:
        challenge = base64.urlsafe_b64decode(
            encoded + "=" * (-len(encoded) % 4)
        )
    except (ValueError, TypeError):
        raise ValidationError("Invalid Owner WebAuthn authentication challenge.")
    raw_id = credential.get("rawId") if isinstance(credential, dict) else None
    if not raw_id:
        raise ValidationError("WebAuthn credential ID is required.")
    try:
        credential_id = base64.urlsafe_b64decode(raw_id + "=" * (-len(raw_id) % 4))
    except (ValueError, TypeError):
        raise ValidationError("Invalid WebAuthn credential ID.")
    stored = (
        OwnerWebAuthnCredential.objects.select_for_update()
        .filter(
            owner_entity=entity,
            credential_id=credential_id,
            revoked_at__isnull=True,
        )
        .first()
    )
    if not stored:
        raise ValidationError("Unknown or revoked Owner passkey.")
    _consume_challenge(
        request, entity, OwnerWebAuthnChallenge.Ceremony.AUTHENTICATION, challenge
    )
    verification = verify_authentication_response(
        credential=credential,
        expected_challenge=challenge,
        expected_origin=settings.OWNER_WEBAUTHN_ORIGINS,
        expected_rp_id=settings.OWNER_WEBAUTHN_RP_ID,
        credential_public_key=stored.public_key,
        credential_current_sign_count=stored.sign_count,
        require_user_verification=True,
    )
    if verification.credential_id != stored.credential_id:
        raise ValidationError("WebAuthn credential mismatch.")
    if isinstance(credential, dict):
        user_handle = credential.get("response", {}).get("userHandle")
        if user_handle:
            returned_handle = base64.urlsafe_b64decode(
                user_handle + "=" * (-len(user_handle) % 4)
            )
            if returned_handle != entity.webauthn_user_handle:
                raise ValidationError("WebAuthn user handle mismatch.")
    if verification.new_sign_count < stored.sign_count:
        raise ValidationError("WebAuthn signature counter moved backwards.")
    stored.sign_count = verification.new_sign_count
    stored.backed_up = verification.credential_backed_up
    stored.last_used_at = timezone.now()
    stored.save(
        update_fields=(
            "sign_count",
            "backed_up",
            "last_used_at",
        )
    )
    bind_owner_session_webauthn(request, owner_user, stored.pk)
    return stored
