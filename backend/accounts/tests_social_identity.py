from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.test import TestCase

from accounts.models import AccountEntity, OwnerSocialIdentity
from accounts.social_identity import bind_verified_owner_social_identity


class OwnerSocialIdentityBindingSecurityTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="social-owner",
            password="test-password-123",
        )
        self.owner_entity = AccountEntity.objects.create(
            user=self.owner,
            entity_type=AccountEntity.EntityType.WORKER,
            identity_email="social-owner@example.test",
        )

    def test_verified_identity_is_created_for_owner(self):
        identity = bind_verified_owner_social_identity(
            self.owner_entity,
            OwnerSocialIdentity.Provider.FACEBOOK,
            "fb-123",
            "owner",
        )

        self.assertEqual(identity.account_entity_id, self.owner_entity.pk)
        self.assertEqual(identity.provider_user_id, "fb-123")
        self.assertEqual(identity.username, "owner")
        self.assertIsNotNone(identity.verified_at)

    def test_existing_owner_identity_is_updated_and_verified(self):
        identity = OwnerSocialIdentity.objects.create(
            account_entity=self.owner_entity,
            provider=OwnerSocialIdentity.Provider.INSTAGRAM,
            provider_user_id="ig-123",
        )

        updated = bind_verified_owner_social_identity(
            self.owner_entity,
            OwnerSocialIdentity.Provider.INSTAGRAM,
            "ig-123",
            "owner_ig",
        )

        self.assertEqual(updated.pk, identity.pk)
        updated.refresh_from_db()
        self.assertEqual(updated.username, "owner_ig")
        self.assertIsNotNone(updated.verified_at)

    def test_identity_already_bound_to_another_entity_is_rejected(self):
        other_user = User.objects.create_user(
            username="other-owner",
            password="test-password-123",
        )
        other_entity = AccountEntity.objects.create(
            user=other_user,
            entity_type=AccountEntity.EntityType.OWNER,
            identity_email="other@example.test",
        )
        OwnerSocialIdentity.objects.bulk_create(
            [
                OwnerSocialIdentity(
                    account_entity=other_entity,
                    provider=OwnerSocialIdentity.Provider.FACEBOOK,
                    provider_user_id="fb-duplicate",
                )
            ]
        )

        with self.assertRaises(ValidationError):
            bind_verified_owner_social_identity(
                self.owner_entity,
                OwnerSocialIdentity.Provider.FACEBOOK,
                "fb-duplicate",
            )

    def test_non_owner_entity_cannot_bind_identity(self):
        worker = User.objects.create_user(
            username="social-worker",
            password="test-password-123",
        )
        worker_entity = AccountEntity.objects.create(
            user=worker,
            entity_type=AccountEntity.EntityType.WORKER,
            identity_email="worker@example.test",
        )

        with self.assertRaises(PermissionError):
            bind_verified_owner_social_identity(
                worker_entity,
                OwnerSocialIdentity.Provider.FACEBOOK,
                "fb-worker",
            )

    def test_empty_provider_identity_is_rejected(self):
        with self.assertRaises(ValidationError):
            bind_verified_owner_social_identity(
                self.owner_entity,
                OwnerSocialIdentity.Provider.FACEBOOK,
                "",
            )
