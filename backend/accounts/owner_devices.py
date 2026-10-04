import hashlib
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import AccountEntity, OwnerTrustedDevice
from .policies import is_owner

MAX_ACTIVE_OWNER_DEVICES = 3


def hash_device_identifier(device_identifier):
    if not isinstance(device_identifier, str) or not device_identifier.strip():
        raise ValidationError("A device identifier is required.")
    return hashlib.sha256(device_identifier.strip().encode("utf-8")).hexdigest()


@transaction.atomic
def bind_owner_device(owner_user, device_identifier, label=""):
    """Create a trusted Owner device binding without storing the raw identifier."""
    if not is_owner(owner_user):
        raise PermissionError("Only the canonical active Owner can bind devices.")

    owner_entity = AccountEntity.objects.select_for_update().get(
        user=owner_user,
        entity_type=AccountEntity.EntityType.OWNER,
        is_active=True,
    )

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
        status=device_model.Status.ACTIVE,
    ).count()
    if active_count >= MAX_ACTIVE_OWNER_DEVICES:
        raise ValidationError(
            "The Owner already has the maximum of 3 active trusted devices."
        )

    return OwnerTrustedDevice.objects.create(
        owner_entity=owner_entity,
        device_identifier_hash=device_hash,
        label=label[:100],
        status=device_model.Status.ACTIVE,
        approved_at=timezone.now(),
    )


@transaction.atomic
def revoke_owner_device(owner_user, device_id):
    if not is_owner(owner_user):
        raise PermissionError("Only the canonical active Owner can revoke devices.")

    owner_entity = AccountEntity.objects.select_for_update().get(
        user=owner_user,
        entity_type=AccountEntity.EntityType.OWNER,
        is_active=True,
    )
    device = device_model.objects.select_for_update().filter(
        pk=device_id,
        owner_entity=owner_entity,
        status=device_model.Status.ACTIVE,
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
        status=device_model.Status.ACTIVE,
    ).order_by("-last_seen_at", "-created_at")
