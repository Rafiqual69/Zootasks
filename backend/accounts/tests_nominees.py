from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from .models import AccountEntity, OwnerNominee
from .owner_nominees import appoint_owner_nominee, revoke_owner_nominee


@override_settings(OWNER_USERNAME="owner-test")
class OwnerNomineeTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user(
            username="owner-test",
            password="Strong-Test-Password-123!",
            is_staff=True,
            is_superuser=True,
        )
        self.owner_entity = AccountEntity.objects.create(
            user=self.owner,
            entity_type=AccountEntity.EntityType.OWNER,
            identity_email="owner@example.com",
        )
        self.nominees = [
            User.objects.create_user(username=f"nominee-{i}")
            for i in range(1, 7)
        ]

    def test_owner_can_appoint_six_nominees(self):
        for order, user in enumerate(self.nominees, start=1):
            appoint_owner_nominee(self.owner, user, order)
        self.assertEqual(
            OwnerNominee.objects.filter(owner_entity=self.owner_entity, is_active=True).count(),
            6,
        )

    def test_seventh_active_nominee_is_rejected(self):
        for order, user in enumerate(self.nominees, start=1):
            appoint_owner_nominee(self.owner, user, order)
        extra = get_user_model().objects.create_user(username="nominee-7")
        with self.assertRaises(ValidationError):
            appoint_owner_nominee(self.owner, extra, 1)

    def test_only_one_active_super_nominee(self):
        first = appoint_owner_nominee(self.owner, self.nominees[0], 1, super_nominee=True)
        second = appoint_owner_nominee(self.owner, self.nominees[1], 2, super_nominee=True)
        first.refresh_from_db()
        self.assertEqual(first.role, OwnerNominee.Role.NOMINEE)
        self.assertEqual(second.role, OwnerNominee.Role.SUPER_NOMINEE)

    def test_owner_cannot_be_nominee(self):
        with self.assertRaises(ValidationError):
            appoint_owner_nominee(self.owner, self.owner, 1)

    def test_non_owner_cannot_appoint(self):
        with self.assertRaises(PermissionError):
            appoint_owner_nominee(self.nominees[0], self.nominees[1], 1)

    def test_revocation_is_auditable_and_frees_active_slot(self):
        nominee = appoint_owner_nominee(self.owner, self.nominees[0], 1)
        revoke_owner_nominee(self.owner, nominee.pk)
        nominee.refresh_from_db()
        self.assertFalse(nominee.is_active)
        self.assertIsNotNone(nominee.revoked_at)

        replacement = appoint_owner_nominee(self.owner, self.nominees[1], 1)
        self.assertTrue(replacement.is_active)
        self.assertEqual(replacement.succession_order, 1)
