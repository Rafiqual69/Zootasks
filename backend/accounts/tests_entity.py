from django.contrib import admin
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from accounts.admin import AccountEntityAdmin
from accounts.models import (
    AccountEntity,
    AdvertiserProfile,
    OwnerIdentityBinding,
    TelegramIdentity,
)


class AccountEntitySecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="entity-worker",
            password="test-password-123",
        )
        self.entity = AccountEntity.objects.create(
            user=self.user,
            entity_type=AccountEntity.EntityType.WORKER,
            identity_email="worker@example.test",
        )

    def test_entity_is_one_to_one_with_user(self):
        self.assertEqual(self.entity.user_id, self.user.id)
        self.assertEqual(
            AccountEntity.objects.get(user=self.user).pk,
            self.entity.pk,
        )

    def test_identity_email_is_unique(self):
        other = User.objects.create_user(
            username="entity-other",
            password="test-password-123",
        )
        with self.assertRaises(Exception):
            AccountEntity.objects.create(
                user=other,
                entity_type=AccountEntity.EntityType.WORKER,
                identity_email="worker@example.test",
            )

    def test_advertiser_profile_is_one_to_one_and_protected(self):
        advertiser = User.objects.create_user(
            username="entity-advertiser",
            password="test-password-123",
        )
        profile = AdvertiserProfile.objects.create(
            user=advertiser,
            organization_name="Test Advertiser",
            contact_name="Owner",
        )

        self.assertEqual(profile.user_id, advertiser.id)
        self.assertEqual(
            AdvertiserProfile.objects.get(user=advertiser).pk,
            profile.pk,
        )

        from accounts.admin import AdvertiserProfileAdmin

        request = type("Request", (), {})()
        request.user = self.user
        model_admin = AdvertiserProfileAdmin(AdvertiserProfile, admin.site)

        self.assertFalse(model_admin.has_add_permission(request))
        self.assertFalse(model_admin.has_change_permission(request, profile))
        self.assertFalse(model_admin.has_delete_permission(request, profile))

    def test_account_entity_admin_is_read_only(self):
        request = type("Request", (), {})()
        request.user = User.objects.create_superuser(
            username="audit-superuser",
            password="test-password-123",
        )
        model_admin = AccountEntityAdmin(AccountEntity, admin.site)

        self.assertFalse(model_admin.has_add_permission(request))
        self.assertFalse(model_admin.has_change_permission(request, self.entity))
        self.assertFalse(model_admin.has_delete_permission(request, self.entity))

        for field_name in (
            "user",
            "entity_type",
            "identity_email",
            "email_verified_at",
            "is_active",
            "created_at",
            "updated_at",
        ):
            self.assertIn(field_name, model_admin.readonly_fields)

    def test_owner_identity_binding_accepts_only_owner_entity(self):
        owner = User.objects.create_user(
            username="binding-owner",
            password="test-password-123",
        )
        owner_entity = AccountEntity.objects.create(
            user=owner,
            entity_type=AccountEntity.EntityType.OWNER,
            identity_email="binding-owner@example.test",
        )

        binding = OwnerIdentityBinding.objects.create(
            account_entity=owner_entity,
            mobile_number="+8801000000000",
        )

        self.assertEqual(binding.account_entity_id, owner_entity.id)

    def test_owner_identity_binding_rejects_non_owner_entity(self):
        with self.assertRaises(ValidationError):
            OwnerIdentityBinding.objects.create(
                account_entity=self.entity,
                mobile_number="+8801000000001",
            )

    def test_owner_mobile_number_is_unique(self):
        owner = User.objects.create_user(
            username="binding-owner-unique",
            password="test-password-123",
        )
        owner_entity = AccountEntity.objects.create(
            user=owner,
            entity_type=AccountEntity.EntityType.OWNER,
            identity_email="binding-owner-unique@example.test",
        )
        OwnerIdentityBinding.objects.create(
            account_entity=owner_entity,
            mobile_number="+8801000000002",
        )

        other = User.objects.create_user(
            username="binding-owner-other",
            password="test-password-123",
        )
        other_entity = AccountEntity.objects.create(
            user=other,
            entity_type=AccountEntity.EntityType.SUPER_ADMIN,
            identity_email="binding-owner-other@example.test",
        )

        with self.assertRaises(Exception):
            OwnerIdentityBinding.objects.create(
                account_entity=other_entity,
                mobile_number="+8801000000002",
            )

    def test_owner_telegram_binding_is_one_to_one(self):
        owner = User.objects.create_user(
            username="binding-telegram-owner",
            password="test-password-123",
        )
        owner_entity = AccountEntity.objects.create(
            user=owner,
            entity_type=AccountEntity.EntityType.OWNER,
            identity_email="binding-telegram-owner@example.test",
        )
        telegram = TelegramIdentity.objects.create(
            user=owner,
            telegram_user_id=900000001,
            verified_at=None,
        )

        binding = OwnerIdentityBinding.objects.create(
            account_entity=owner_entity,
            telegram_identity=telegram,
        )

        self.assertEqual(binding.telegram_identity_id, telegram.id)
