from django.contrib.auth import get_user_model

from .models import AccountEntity


def is_owner(user):
    """Return True only for the canonical active Owner entity."""
    if not user or not getattr(user, "is_authenticated", False):
        return False

    User = get_user_model()
    if not isinstance(user, User):
        return False

    return AccountEntity.objects.filter(
        user=user,
        entity_type=AccountEntity.EntityType.OWNER,
        is_active=True,
    ).exists()


def is_worker(user):
    """Return True only for an account allowed to perform worker actions."""
    if not user or not getattr(user, "is_authenticated", False):
        return False

    User = get_user_model()
    if not isinstance(user, User):
        return False

    from .models import WorkerProfile

    if not WorkerProfile.objects.filter(user=user).exists():
        return False

    entity = AccountEntity.objects.filter(user=user).first()
    if entity is None:
        # Transitional compatibility for legacy worker records.
        return True

    return (
        entity.entity_type == AccountEntity.EntityType.WORKER
        and entity.is_active
    )
