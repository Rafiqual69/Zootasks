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
