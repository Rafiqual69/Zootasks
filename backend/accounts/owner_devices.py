import hashlib
import secrets
from datetime import timedelta

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import AccountEntity, OwnerTrustedDevice
from .policies import is_owner

MAX_ACTIVE_OWNER_DEVICES = 3
ENROLLMENT_TTL = timedelta(minutes=10)


def hash_device_identifier(device_identifier):
    if not isinstance(device_identifier, str) or not device_identifier.strip():
        raise ValidationError("A device identifier is required.")
    return hashlib.sha256(device_identifier.strip().encode("utf-8")).hexdigest()


def _validate_public_key(public_key):
    if not isinstance(public_key, bytes) or len(public_key) != 32:
        raise ValidationError("Owner device public key must be exactly 32 bytes.")
    try:
        Ed25519PublicKey.from_public_bytes(public_key)
    except ValueError as exc:
        raise ValidationError("Invalid Owner device public key.") from exc
    return public_key


def _hash_challenge(challenge):
    return hashlib.sha256(challenge).hexdigest()


@transaction.atomic
def bind_owner_device(owner_user, device_identifier, public_key, label=""):
    """Direct Owner-controlled enrollment of a cryptographically bound device."""
    if not is_owner(owner_user):
        raise PermissionError("Only the canonical active Owner can bind devices.")

    owner_entity = AccountEntity.objects.select_for_update().get(
        user=owner_user,
        entity_type=AccountEntity.EntityType.OWNER,
        is_active=True,
    )
    public_key = _validate_public_key(public_key)
    device_hash = hash_device_identifier(device_identifier)

    existing = OwnerTrustedDevice.objects.filter(
        owner_entity=owner_entity,
        device_identifier_hash=device_hash,
        status=OwnerTrustedDevice.Status.ACTIVE,
    ).first()
    if existing:
        existing.last_seen_at = timezone.now()
        existing.save(update_fields=("last_seen_at", "updated_at"))
        return existing

    active_count = OwnerTrustedDevice.objects.filter(
        owner_entity=owner_entity,
        status=OwnerTrustedDevice.Status.ACTIVE,
    ).count()
    if active_count >= MAX_ACTIVE_OWNER_DEVICES:
        raise ValidationError(
            "The Owner already has the maximum of 3 active trusted devices."
        )

    return OwnerTrustedDevice.objects.create(
        owner_entity=owner_entity,
        device_identifier_hash=device_hash,
        public_key=public_key,
        label=label[:100],
        status=OwnerTrustedDevice.Status.ACTIVE,
        approved_at=timezone.now(),
    )


@transaction.atomic
def request_owner_device_enrollment(owner_user, device_identifier, public_key, label=""):
    """Create a one-time pending enrollment challenge for a new device."""
    if not is_owner(owner_user):
        raise PermissionError("Only the canonical active Owner can request device enrollment.")

    owner_entity = AccountEntity.objects.select_for_update().get(
        user=owner_user,
        entity_type=AccountEntity.EntityType.OWNER,
        is_active=True,
    )
    public_key = _validate_public_key(public_key)
    device_hash = hash_device_identifier(device_identifier)

    if OwnerTrustedDevice.objects.filter(
        owner_entity=owner_entity,
        device_identifier_hash=device_hash,
        status=OwnerTrustedDevice.Status.ACTIVE,
    ).exists():
        raise ValidationError("This device is already trusted.")

    active_count = OwnerTrustedDevice.objects.filter(
        owner_entity=owner_entity,
        status=OwnerTrustedDevice.Status.ACTIVE,
    ).count()
    if active_count >= MAX_ACTIVE_OWNER_DEVICES:
        raise ValidationError(
            "The Owner already has the maximum of 3 active trusted devices."
        )

    now = timezone.now()
    challenge = secrets.token_bytes(32)
    device = OwnerTrustedDevice.objects.create(
        owner_entity=owner_entity,
        device_identifier_hash=device_hash,
        public_key=public_key,
        label=label[:100],
        status=OwnerTrustedDevice.Status.PENDING,
        enrollment_challenge_hash=_hash_challenge(challenge),
        enrollment_challenge_expires_at=now + ENROLLMENT_TTL,
    )
    return device, challenge


@transaction.atomic
def approve_owner_device(owner_user, device_id, challenge_signature):
    """Owner approves a pending device only after proof of private-key possession."""
    if not is_owner(owner_user):
        raise PermissionError("Only the canonical active Owner can approve devices.")
    if not isinstance(challenge_signature, bytes) or not challenge_signature:
        raise ValidationError("A device challenge signature is required.")

    owner_entity = AccountEntity.objects.select_for_update().get(
        user=owner_user,
        entity_type=AccountEntity.EntityType.OWNER,
        is_active=True,
    )
    device = OwnerTrustedDevice.objects.select_for_update().filter(
        pk=device_id,
        owner_entity=owner_entity,
        status=OwnerTrustedDevice.Status.PENDING,
    ).first()
    if device is None:
        raise ValidationError("Pending trusted device not found.")

    now = timezone.now()
    if not device.enrollment_challenge_hash or not device.enrollment_challenge_expires_at:
        raise ValidationError("Device enrollment challenge is unavailable.")
    if device.enrollment_challenge_expires_at <= now:
        raise ValidationError("Device enrollment challenge has expired.")

    challenge = None
    # The raw challenge is deliberately never persisted. The caller must provide
    # the original challenge bytes alongside the signature via the verifier below.
    raise ValidationError("Use approve_owner_device_with_challenge for enrollment approval.")


@transaction.atomic
def approve_owner_device_with_challenge(owner_user, device_id, challenge, challenge_signature):
    """Approve a pending device using a one-time Ed25519 challenge response."""
    if not is_owner(owner_user):
        raise PermissionError("Only the canonical active Owner can approve devices.")
    if not isinstance(challenge, bytes) or len(challenge) != 32:
        raise ValidationError("A valid 32-byte enrollment challenge is required.")
    if not isinstance(challenge_signature, bytes) or not challenge_signature:
        raise ValidationError("A device challenge signature is required.")

    owner_entity = AccountEntity.objects.select_for_update().get(
        user=owner_user,
        entity_type=AccountEntity.EntityType.OWNER,
        is_active=True,
    )
    device = OwnerTrustedDevice.objects.select_for_update().filter(
        pk=device_id,
        owner_entity=owner_entity,
        status=OwnerTrustedDevice.Status.PENDING,
    ).first()
    if device is None:
        raise ValidationError("Pending trusted device not found.")

    now = timezone.now()
    if device.enrollment_challenge_expires_at <= now:
        raise ValidationError("Device enrollment challenge has expired.")
    if not device.enrollment_challenge_hash or not secrets.compare_digest(
        device.enrollment_challenge_hash, _hash_challenge(challenge)
    ):
        raise ValidationError("Invalid or replayed device enrollment challenge.")

    try:
        Ed25519PublicKey.from_public_bytes(device.public_key).verify(
            challenge_signature, challenge
        )
    except (ValueError, TypeError):
        raise ValidationError("Invalid device challenge signature.")

    active_count = OwnerTrustedDevice.objects.filter(
        owner_entity=owner_entity,
        status=OwnerTrustedDevice.Status.ACTIVE,
    ).count()
    if active_count >= MAX_ACTIVE_OWNER_DEVICES:
        raise ValidationError("The Owner already has the maximum of 3 active trusted devices.")

    device.status = OwnerTrustedDevice.Status.ACTIVE
    device.approved_at = now
    device.enrollment_challenge_hash = None
    device.enrollment_challenge_expires_at = None
    device.last_seen_at = now
    device.save(update_fields=(
        "status", "approved_at", "enrollment_challenge_hash",
        "enrollment_challenge_expires_at", "last_seen_at", "updated_at",
    ))
    return device


@transaction.atomic
def revoke_owner_device(owner_user, device_id):
    if not is_owner(owner_user):
        raise PermissionError("Only the canonical active Owner can revoke devices.")

    owner_entity = AccountEntity.objects.select_for_update().get(
        user=owner_user,
        entity_type=AccountEntity.EntityType.OWNER,
        is_active=True,
    )
    device = OwnerTrustedDevice.objects.select_for_update().filter(
        pk=device_id,
        owner_entity=owner_entity,
        status=OwnerTrustedDevice.Status.ACTIVE,
    ).first()
    if device is None:
        raise ValidationError("Active trusted device not found.")

    device.status = OwnerTrustedDevice.Status.REVOKED
    device.revoked_at = timezone.now()
    device.save(update_fields=("status", "revoked_at", "updated_at"))
    return device


def active_owner_devices(owner_user):
    if not is_owner(owner_user):
        raise PermissionError("Only the canonical active Owner can view trusted devices.")

    owner_entity = AccountEntity.objects.get(
        user=owner_user,
        entity_type=AccountEntity.EntityType.OWNER,
        is_active=True,
    )
    return OwnerTrustedDevice.objects.filter(
        owner_entity=owner_entity,
        status=OwnerTrustedDevice.Status.ACTIVE,
    ).order_by("-last_seen_at", "-created_at")
