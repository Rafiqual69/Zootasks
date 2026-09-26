from django.contrib import admin
from django.contrib.auth.models import User
from django.test import TestCase

from accounts.admin import AccountEntityAdmin
from accounts.models import AccountEntity


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
