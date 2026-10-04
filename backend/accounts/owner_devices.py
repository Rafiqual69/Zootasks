import hashlib
import secrets

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import AccountEntity
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
    device_model = __import__("accounts.models", fromlist=["OwnerTrustedDevice"]).OwnerTrustedDevice

    existing = device_model.objects.filter(
        owner_entity=owner_entity,
        device_identifier_hash=device_hash,
        status=device_model.Status.ACTIVE,
    ).first()
    if existing:
        existing.last_seen_at = timezone.now()
        existing.save(update_fields=("last_seen_at", "updated_at"))
        return existing

    active_count = device_model.objects.filter(
        owner_entity=owner_entity,
        status=device_model.Status.ACTIVE,
    ).count()
    if active_count >= MAX_ACTIVE_OWNER_DEVICES:
        raise ValidationError(
            "The Owner already has the maximum of 3 active trusted devices."
        )

    return device_model.objects.create(
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
    device_model = __import__("accounts.models", fromlist=["OwnerTrustedDevice"]).OwnerTrustedDevice
    device = device_model.objects.select_for_update().filter(
        pk=device_id,
        owner_entity=owner_entity,
        status=device_model.Status.ACTIVE,
    ).first()
    if device is None:
        raise ValidationError("Active trusted device not found.")

    device.status = device_model.Status.REVOKED
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
    device_model = __import__("accounts.models", fromlist=["OwnerTrustedDevice"]).OwnerTrustedDevice
    return device_model.objects.filter(
        owner_entity=owner_entity,
        status=device_model.Status.ACTIVE,
    ).order_by("-last_seen_at", "-created_at")
