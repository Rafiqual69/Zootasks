import hashlib
import secrets
from datetime import timedelta

from django.conf import settings

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import AccountEntity, OwnerSessionBinding, OwnerTrustedDevice, OwnerWebAuthnCredential
from .policies import is_owner


SESSION_BINDING_SESSION_KEY = "owner_session_binding"
BINDING_TOKEN_BYTES = 32


def _hash(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _session_key_hash(session_key):
    if not isinstance(session_key, str) or not session_key:
        raise ValidationError("An established Django session is required.")
    return _hash(session_key)


def _binding_token_hash(token):
    return _hash(token)


@transaction.atomic
def bind_owner_session(request, owner_user, trusted_device_id):
    """Bind the current authenticated Owner session to an active trusted device."""
    if not getattr(request.user, "is_authenticated", False):
        raise PermissionError("An authenticated Owner session is required.")
    if request.user.pk != owner_user.pk:
        raise PermissionError("The session user must match the Owner being bound.")
    if not is_owner(owner_user):
        raise PermissionError("Only the canonical active Owner can bind a session.")

    session_key = request.session.session_key
    session_hash = _session_key_hash(session_key)

    owner_entity = AccountEntity.objects.select_for_update().get(
        user=owner_user,
        entity_type=AccountEntity.EntityType.OWNER,
        is_active=True,
    )
    device = OwnerTrustedDevice.objects.select_for_update().filter(
        pk=trusted_device_id,
        owner_entity=owner_entity,
        status=OwnerTrustedDevice.Status.ACTIVE,
    ).first()
    if device is None:
        raise ValidationError("Active trusted device not found.")

    now = timezone.now()
    OwnerSessionBinding.objects.select_for_update().filter(
        owner_entity=owner_entity,
        session_key_hash=session_hash,
        revoked_at__isnull=True,
    ).update(revoked_at=now)

    token = secrets.token_urlsafe(BINDING_TOKEN_BYTES)
    binding = OwnerSessionBinding.objects.create(
        owner_entity=owner_entity,
        trusted_device=device,
        binding_token_hash=_binding_token_hash(token),
        session_key_hash=session_hash,
        last_seen_at=now,
        expires_at=now + timedelta(seconds=settings.OWNER_SESSION_BINDING_TTL_SECONDS),
    )

    request.session[SESSION_BINDING_SESSION_KEY] = token
    request.session.modified = True
    return binding



@transaction.atomic
def bind_owner_session_webauthn(request, owner_user, webauthn_credential_id):
    """Bind the current Owner session to a verified active WebAuthn credential."""
    if not getattr(request.user, "is_authenticated", False):
        raise PermissionError("An authenticated Owner session is required.")
    if request.user.pk != owner_user.pk:
        raise PermissionError("The session user must match the Owner being bound.")
    if not is_owner(owner_user):
        raise PermissionError("Only the canonical active Owner can bind a session.")

    session_key = request.session.session_key
    session_hash = _session_key_hash(session_key)
    owner_entity = AccountEntity.objects.select_for_update().get(
        user=owner_user,
        entity_type=AccountEntity.EntityType.OWNER,
        is_active=True,
    )
    credential = OwnerWebAuthnCredential.objects.select_for_update().filter(
        pk=webauthn_credential_id,
        owner_entity=owner_entity,
        revoked_at__isnull=True,
    ).first()
    if credential is None:
        raise ValidationError("Active Owner WebAuthn credential not found.")

    now = timezone.now()
    OwnerSessionBinding.objects.select_for_update().filter(
        owner_entity=owner_entity,
        session_key_hash=session_hash,
        revoked_at__isnull=True,
    ).update(revoked_at=now)

    token = secrets.token_urlsafe(BINDING_TOKEN_BYTES)
    binding = OwnerSessionBinding.objects.create(
        owner_entity=owner_entity,
        webauthn_credential=credential,
        binding_token_hash=_binding_token_hash(token),
        session_key_hash=session_hash,
        last_seen_at=now,
    )
    request.session[SESSION_BINDING_SESSION_KEY] = token
    request.session.modified = True
    return binding

def get_current_owner_session_binding(request):
    """Return the current valid Owner session binding, or None on any mismatch."""
    if not getattr(request.user, "is_authenticated", False):
        return None
    if not is_owner(request.user):
        return None

    token = request.session.get(SESSION_BINDING_SESSION_KEY)
    session_key = request.session.session_key
    if not token or not session_key:
        return None

    owner_entity = AccountEntity.objects.filter(
        user=request.user,
        entity_type=AccountEntity.EntityType.OWNER,
        is_active=True,
    ).first()
    if owner_entity is None:
        return None

    binding = (
        OwnerSessionBinding.objects
        .select_related("trusted_device", "webauthn_credential")
        .filter(
            owner_entity=owner_entity,
            binding_token_hash=_binding_token_hash(token),
            session_key_hash=_session_key_hash(session_key),
            revoked_at__isnull=True,
        )
        .first()
    )
    if binding is None or not binding.is_active:
        return None
    return binding


def is_owner_session_bound(request):
    return get_current_owner_session_binding(request) is not None


@transaction.atomic
def revoke_owner_session_binding(request):
    """Revoke the current server-side binding and remove its session reference."""
    token = request.session.get(SESSION_BINDING_SESSION_KEY)
    session_key = request.session.session_key
    if token and session_key:
        OwnerSessionBinding.objects.filter(
            binding_token_hash=_binding_token_hash(token),
            session_key_hash=_session_key_hash(session_key),
            revoked_at__isnull=True,
        ).update(revoked_at=timezone.now())

    request.session.pop(SESSION_BINDING_SESSION_KEY, None)
    request.session.modified = True
