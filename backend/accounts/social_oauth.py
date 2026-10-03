import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import AccountEntity, OwnerSocialIdentity, OwnerSocialOAuthState
from .policies import is_owner


def _hash_state(state):
    return hashlib.sha256(state.encode("utf-8")).hexdigest()


def issue_owner_social_oauth_state(user, provider):
    if provider not in OwnerSocialIdentity.Provider.values:
        raise ValueError("Unsupported Owner social provider.")
    if not is_owner(user):
        raise PermissionError("Canonical active Owner access is required.")

    ttl_seconds = getattr(settings, "OWNER_SOCIAL_OAUTH_STATE_TTL_SECONDS", 600)
    if ttl_seconds <= 0:
        raise ValueError("Owner social OAuth state TTL must be positive.")

    raw_state = secrets.token_urlsafe(32)
    now = timezone.now()

    with transaction.atomic():
        owner_entity = AccountEntity.objects.select_for_update().get(
            user=user,
            entity_type=AccountEntity.EntityType.OWNER,
            is_active=True,
        )
        OwnerSocialOAuthState.objects.create(
            account_entity=owner_entity,
            provider=provider,
            state_hash=_hash_state(raw_state),
            expires_at=now + timedelta(seconds=ttl_seconds),
        )

    return raw_state


def consume_owner_social_oauth_state(raw_state, provider):
    if not raw_state:
        return None
    if provider not in OwnerSocialIdentity.Provider.values:
        raise ValueError("Unsupported Owner social provider.")

    state_hash = _hash_state(raw_state)

    with transaction.atomic():
        challenge = (
            OwnerSocialOAuthState.objects.select_for_update()
            .select_related("account_entity")
            .filter(
                state_hash=state_hash,
                provider=provider,
                account_entity__entity_type=AccountEntity.EntityType.OWNER,
                account_entity__is_active=True,
            )
            .first()
        )
        if challenge is None or not challenge.is_valid():
            return None

        challenge.used_at = timezone.now()
        challenge.save(update_fields=["used_at"])
        return challenge.account_entity
