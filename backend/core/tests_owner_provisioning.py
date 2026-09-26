from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from accounts.models import AccountEntity


class OwnerProvisioningCommandTests(TestCase):
    @override_settings(
        OWNER_USERNAME="owner-provision-test",
        OWNER_IDENTITY_EMAIL="owner@example.test",
    )
    def test_provisions_existing_privileged_owner_without_creating_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="owner-provision-test",
            password="test-password-123",
            is_staff=True,
            is_superuser=True,
        )

        call_command("provision_owner", confirm=True)

        self.assertEqual(User.objects.count(), 1)
        entity = AccountEntity.objects.get(user=user)
        self.assertEqual(entity.entity_type, AccountEntity.EntityType.OWNER)
        self.assertEqual(entity.identity_email, "owner@example.test")
        self.assertTrue(entity.is_active)
        self.assertIsNone(entity.email_verified_at)

    @override_settings(
        OWNER_USERNAME="missing-owner",
        OWNER_IDENTITY_EMAIL="owner@example.test",
    )
    def test_fails_if_configured_owner_user_does_not_exist(self):
        with self.assertRaises(CommandError):
            call_command("provision_owner", confirm=True)

        self.assertEqual(AccountEntity.objects.count(), 0)

    @override_settings(
        OWNER_USERNAME="owner-provision-test",
        OWNER_IDENTITY_EMAIL="owner@example.test",
    )
    def test_fails_without_explicit_confirmation(self):
        User = get_user_model()
        User.objects.create_user(
            username="owner-provision-test",
            password="test-password-123",
            is_staff=True,
            is_superuser=True,
        )

        with self.assertRaises(CommandError):
            call_command("provision_owner")

        self.assertEqual(AccountEntity.objects.count(), 0)

    @override_settings(
        OWNER_USERNAME="owner-provision-test",
        OWNER_IDENTITY_EMAIL="owner@example.test",
    )
    def test_fails_for_non_privileged_configured_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="owner-provision-test",
            password="test-password-123",
        )

        with self.assertRaises(CommandError):
            call_command("provision_owner", confirm=True)

        self.assertFalse(AccountEntity.objects.filter(user=user).exists())

    @override_settings(
        OWNER_USERNAME="owner-provision-test",
        OWNER_IDENTITY_EMAIL="owner@example.test",
    )
    def test_fails_if_configured_user_already_has_entity(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="owner-provision-test",
            password="test-password-123",
            is_staff=True,
            is_superuser=True,
        )
        AccountEntity.objects.create(
            user=user,
            entity_type=AccountEntity.EntityType.SUPER_ADMIN,
        )

        with self.assertRaises(CommandError):
            call_command("provision_owner", confirm=True)

        self.assertEqual(AccountEntity.objects.count(), 1)

    @override_settings(
        OWNER_USERNAME="owner-provision-test",
        OWNER_IDENTITY_EMAIL="owner@example.test",
    )
    def test_fails_if_another_owner_already_exists(self):
        User = get_user_model()
        existing_owner = User.objects.create_user(
            username="existing-owner",
            password="test-password-123",
            is_staff=True,
            is_superuser=True,
        )
        target = User.objects.create_user(
            username="owner-provision-test",
            password="test-password-123",
            is_staff=True,
            is_superuser=True,
        )
        AccountEntity.objects.create(
            user=existing_owner,
            entity_type=AccountEntity.EntityType.OWNER,
        )

        with self.assertRaises(CommandError):
            call_command("provision_owner", confirm=True)

        self.assertFalse(AccountEntity.objects.filter(user=target).exists())
        self.assertEqual(
            AccountEntity.objects.filter(
                entity_type=AccountEntity.EntityType.OWNER
            ).count(),
            1,
        )

    @override_settings(
        OWNER_USERNAME="owner-provision-test",
        OWNER_IDENTITY_EMAIL="",
    )
    def test_fails_without_owner_identity_email_configuration(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="owner-provision-test",
            password="test-password-123",
            is_staff=True,
            is_superuser=True,
        )

        with self.assertRaises(CommandError):
            call_command("provision_owner", confirm=True)

        self.assertFalse(AccountEntity.objects.filter(user=user).exists())

    @override_settings(
        OWNER_USERNAME="owner-provision-test",
        OWNER_IDENTITY_EMAIL="owner@example.test",
    )
    def test_is_idempotence_safe_after_first_provisioning(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="owner-provision-test",
            password="test-password-123",
            is_staff=True,
            is_superuser=True,
        )

        call_command("provision_owner", confirm=True)

        with self.assertRaises(CommandError):
            call_command("provision_owner", confirm=True)

        self.assertEqual(AccountEntity.objects.filter(user=user).count(), 1)
        self.assertEqual(
            AccountEntity.objects.filter(
                entity_type=AccountEntity.EntityType.OWNER
            ).count(),
            1,
        )
