from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import AccountEntity, OwnerSocialIdentity
from .policies import is_owner


def bind_verified_owner_social_identity(
    owner_entity,
    provider,
    provider_user_id,
    username="",
):
    if provider not in OwnerSocialIdentity.Provider.values:
        raise ValueError("Unsupported Owner social provider.")
    if not owner_entity or owner_entity.entity_type != AccountEntity.EntityType.OWNER:
        raise PermissionError("Canonical Owner entity is required.")
    if not is_owner(owner_entity.user):
        raise PermissionError("Canonical active Owner access is required.")

    provider_user_id = str(provider_user_id or "").strip()
    if not provider_user_id:
        raise ValidationError("Verified provider user ID is required.")

    username = str(username or "").strip()
    if len(username) > 150:
        raise ValidationError("Provider username is too long.")

    with transaction.atomic():
        owner_entity = AccountEntity.objects.select_for_update().get(
            pk=owner_entity.pk,
            entity_type=AccountEntity.EntityType.OWNER,
            is_active=True,
        )
        identity = (
            OwnerSocialIdentity.objects.select_for_update()
            .filter(
                provider=provider,
                provider_user_id=provider_user_id,
            )
            .first()
        )
        if identity is not None and identity.account_entity_id != owner_entity.pk:
            raise ValidationError(
                "This social identity is already bound to another account."
            )

        now = timezone.now()
        if identity is None:
            identity = OwnerSocialIdentity.objects.create(
                account_entity=owner_entity,
                provider=provider,
                provider_user_id=provider_user_id,
                username=username,
                verified_at=now,
            )
        else:
            identity.username = username
            identity.verified_at = now
            identity.save(update_fields=["username", "verified_at", "updated_at"])

        return identity
