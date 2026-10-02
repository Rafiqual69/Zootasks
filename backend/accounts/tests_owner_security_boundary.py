from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from accounts.models import (
    AccountEntity,
    OwnerEmailVerificationChallenge,
    OwnerIdentityBinding,
    OwnerSocialIdentity,
    OwnerSocialOAuthState,
)
from accounts.policies import is_owner
from accounts.email_verification import _hash_token, verify_owner_email_token


class OwnerSecurityBoundaryTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user(
            username="owner-boundary",
            password="Strong-Test-Password-123!",
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )
        self.entity = AccountEntity.objects.create(
            user=self.owner,
            entity_type=AccountEntity.EntityType.OWNER,
            identity_email="owner-boundary@example.test",
        )

    def test_owner_policy_rejects_inactive_user(self):
        self.assertTrue(is_owner(self.owner))
        self.owner.is_active = False
        self.owner.save(update_fields=["is_active"])
        self.assertFalse(is_owner(self.owner))

    def test_identity_binding_rejects_inactive_owner_entity(self):
        self.entity.is_active = False
        self.entity.save(update_fields=["is_active"])
        with self.assertRaises(ValidationError):
            OwnerIdentityBinding.objects.create(
                account_entity=self.entity,
                mobile_number="+8801000000011",
            )

    def test_social_identity_rejects_inactive_owner_entity(self):
        self.entity.is_active = False
        self.entity.save(update_fields=["is_active"])
        with self.assertRaises(ValidationError):
            OwnerSocialIdentity.objects.create(
                account_entity=self.entity,
                provider=OwnerSocialIdentity.Provider.FACEBOOK,
                provider_user_id="inactive-owner-facebook",
            )

    def test_oauth_state_rejects_inactive_owner_entity(self):
        self.entity.is_active = False
        self.entity.save(update_fields=["is_active"])
        with self.assertRaises(ValidationError):
            OwnerSocialOAuthState.objects.create(
                account_entity=self.entity,
                provider=OwnerSocialIdentity.Provider.INSTAGRAM,
                state_hash="a" * 64,
                expires_at=timezone.now() + timedelta(minutes=10),
            )

    def test_email_verification_token_cannot_activate_inactive_owner(self):
        token = "inactive-owner-email-token"
        challenge = OwnerEmailVerificationChallenge.objects.create(
            account_entity=self.entity,
            token_hash=_hash_token(token),
            expires_at=timezone.now() + timedelta(minutes=15),
        )
        self.entity.is_active = False
        self.entity.save(update_fields=["is_active"])

        self.assertFalse(verify_owner_email_token(token))
        self.entity.refresh_from_db()
        challenge.refresh_from_db()
        self.assertIsNone(self.entity.email_verified_at)
        self.assertIsNone(challenge.used_at)
