from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.utils import timezone

from accounts.models import AccountEntity, OwnerSocialIdentity, OwnerSocialOAuthState
from accounts.social_oauth import (
    consume_owner_social_oauth_state,
    issue_owner_social_oauth_state,
)


class OwnerSocialOAuthStateSecurityTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="oauth-owner",
            password="test-password-123",
        )
        self.owner_entity = AccountEntity.objects.create(
            user=self.owner,
            entity_type=AccountEntity.EntityType.OWNER,
            identity_email="oauth-owner@example.test",
        )

    @override_settings(OWNER_SOCIAL_OAUTH_STATE_TTL_SECONDS=600)
    def test_state_is_random_and_stored_only_as_hash(self):
        state = issue_owner_social_oauth_state(
            self.owner,
            OwnerSocialIdentity.Provider.FACEBOOK,
        )

        self.assertGreaterEqual(len(state), 32)
        challenge = OwnerSocialOAuthState.objects.get(
            account_entity=self.owner_entity,
        )
        self.assertNotEqual(challenge.state_hash, state)
        self.assertEqual(len(challenge.state_hash), 64)
        self.assertTrue(challenge.is_valid())

    def test_state_can_be_consumed_once_for_matching_provider(self):
        state = issue_owner_social_oauth_state(
            self.owner,
            OwnerSocialIdentity.Provider.INSTAGRAM,
        )

        entity = consume_owner_social_oauth_state(
            state,
            OwnerSocialIdentity.Provider.INSTAGRAM,
        )

        self.assertEqual(entity.pk, self.owner_entity.pk)
        self.assertIsNotNone(
            OwnerSocialOAuthState.objects.get(
                account_entity=self.owner_entity,
            ).used_at
        )
        self.assertIsNone(
            consume_owner_social_oauth_state(
                state,
                OwnerSocialIdentity.Provider.INSTAGRAM,
            )
        )

    def test_state_cannot_be_consumed_for_different_provider(self):
        state = issue_owner_social_oauth_state(
            self.owner,
            OwnerSocialIdentity.Provider.FACEBOOK,
        )

        self.assertIsNone(
            consume_owner_social_oauth_state(
                state,
                OwnerSocialIdentity.Provider.INSTAGRAM,
            )
        )

        challenge = OwnerSocialOAuthState.objects.get(
            account_entity=self.owner_entity,
        )
        self.assertIsNone(challenge.used_at)

    def test_expired_state_is_rejected(self):
        state = issue_owner_social_oauth_state(
            self.owner,
            OwnerSocialIdentity.Provider.FACEBOOK,
        )
        challenge = OwnerSocialOAuthState.objects.get(
            account_entity=self.owner_entity,
        )
        challenge.expires_at = timezone.now() - timedelta(seconds=1)
        challenge.save(update_fields=["expires_at"])

        self.assertIsNone(
            consume_owner_social_oauth_state(
                state,
                OwnerSocialIdentity.Provider.FACEBOOK,
            )
        )

    def test_non_owner_cannot_issue_state(self):
        worker = User.objects.create_user(
            username="oauth-worker",
            password="test-password-123",
        )
        AccountEntity.objects.create(
            user=worker,
            entity_type=AccountEntity.EntityType.WORKER,
            identity_email="oauth-worker@example.test",
        )

        with self.assertRaises(PermissionError):
            issue_owner_social_oauth_state(
                worker,
                OwnerSocialIdentity.Provider.FACEBOOK,
            )

    def test_invalid_provider_is_rejected(self):
        with self.assertRaises(ValueError):
            issue_owner_social_oauth_state(self.owner, "google")

        with self.assertRaises(ValueError):
            consume_owner_social_oauth_state("state", "google")
