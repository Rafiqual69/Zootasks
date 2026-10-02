"""Read-only Owner verification status.

This module reports verification state only. It never grants authorization,
changes credentials, or mutates financial state.
"""
from __future__ import annotations

from dataclasses import dataclass

from django.contrib.auth.models import User

from .models import AccountEntity, OwnerIdentityBinding, OwnerSocialIdentity
from .policies import is_owner

try:
    from django_otp.plugins.otp_totp.models import TOTPDevice
except ImportError:  # pragma: no cover - dependency is present in ZooTasks
    TOTPDevice = None


@dataclass(frozen=True)
class OwnerVerificationSnapshot:
    owner_active: bool
    email_verified: bool
    mobile_verified: bool
    whatsapp_verified: bool
    telegram_verified: bool
    facebook_verified: bool
    instagram_verified: bool
    totp_verified: bool


def get_owner_verification_snapshot(user: User) -> OwnerVerificationSnapshot:
    if not is_owner(user):
        raise PermissionError("Canonical active Owner access is required.")

    entity = AccountEntity.objects.get(
        user=user,
        entity_type=AccountEntity.EntityType.OWNER,
        is_active=True,
    )

    binding = OwnerIdentityBinding.objects.filter(account_entity=entity).first()
    socials = {
        identity.provider: identity
        for identity in OwnerSocialIdentity.objects.filter(
            account_entity=entity,
            verified_at__isnull=False,
        )
    }

    telegram_verified = bool(
        binding
        and binding.telegram_identity_id
        and binding.telegram_identity.verified_at
    )
    totp_verified = bool(
        TOTPDevice is not None
        and TOTPDevice.objects.filter(user=user, confirmed=True).exists()
    )

    return OwnerVerificationSnapshot(
        owner_active=True,
        email_verified=bool(entity.email_verified_at),
        mobile_verified=bool(binding and binding.mobile_verified_at),
        whatsapp_verified=bool(binding and binding.whatsapp_verified_at),
        telegram_verified=telegram_verified,
        facebook_verified=bool(
            socials.get(OwnerSocialIdentity.Provider.FACEBOOK)
        ),
        instagram_verified=bool(
            socials.get(OwnerSocialIdentity.Provider.INSTAGRAM)
        ),
        totp_verified=totp_verified,
    )
