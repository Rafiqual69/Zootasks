from django.core.exceptions import ValidationError
from django.db import transaction
from django.contrib.auth import get_user_model

from .models import AccountEntity, OwnerNominee
from .policies import is_owner


MAX_OWNER_NOMINEES = 6


@transaction.atomic
def appoint_owner_nominee(owner_user, nominee_user, succession_order, *, super_nominee=False):
    """Appoint one of the Owner's six succession nominees.

    This workflow only manages succession identity. It grants no financial
    authority and never changes wallet, withdrawal, or promotion records.
    """
    if not is_owner(owner_user):
        raise PermissionError("Only the canonical active Owner can appoint nominees.")

    if not isinstance(succession_order, int) or not 1 <= succession_order <= MAX_OWNER_NOMINEES:
        raise ValidationError("Succession order must be between 1 and 6.")

    User = get_user_model()
    if not isinstance(nominee_user, User) or not nominee_user.is_active:
        raise ValidationError("Nominee must be an active user account.")

    owner_entity = AccountEntity.objects.select_for_update().get(
        user=owner_user,
        entity_type=AccountEntity.EntityType.OWNER,
        is_active=True,
    )

    active_count = OwnerNominee.objects.filter(
        owner_entity=owner_entity,
        is_active=True,
    ).count()
    existing = OwnerNominee.objects.filter(
        owner_entity=owner_entity,
        succession_order=succession_order,
    ).first()

    if existing is None and active_count >= MAX_OWNER_NOMINEES:
        raise ValidationError("The Owner can have at most 6 active nominees.")

    if existing is not None and existing.nominee_user_id != nominee_user.id:
        raise ValidationError("That succession position is already assigned.")

    role = (
        OwnerNominee.Role.SUPER_NOMINEE
        if super_nominee
        else OwnerNominee.Role.NOMINEE
    )

    if role == OwnerNominee.Role.SUPER_NOMINEE:
        OwnerNominee.objects.filter(
            owner_entity=owner_entity,
            role=OwnerNominee.Role.SUPER_NOMINEE,
            is_active=True,
        ).exclude(pk=getattr(existing, "pk", None)).update(
            role=OwnerNominee.Role.NOMINEE
        )

    nominee = existing or OwnerNominee(
        owner_entity=owner_entity,
        nominee_user=nominee_user,
        succession_order=succession_order,
    )
    nominee.role = role
    nominee.is_active = True
    nominee.revoked_at = None
    nominee.save()
    return nominee


@transaction.atomic
def revoke_owner_nominee(owner_user, nominee_id):
    if not is_owner(owner_user):
        raise PermissionError("Only the canonical active Owner can revoke nominees.")

    owner_entity = AccountEntity.objects.select_for_update().get(
        user=owner_user,
        entity_type=AccountEntity.EntityType.OWNER,
        is_active=True,
    )
    nominee = OwnerNominee.objects.select_for_update().filter(
        pk=nominee_id,
        owner_entity=owner_entity,
        is_active=True,
    ).first()
    if nominee is None:
        raise ValidationError("Active nominee not found.")

    from django.utils import timezone

    nominee.is_active = False
    nominee.revoked_at = timezone.now()
    nominee.save(update_fields=("is_active", "revoked_at", "updated_at"))
    return nominee
