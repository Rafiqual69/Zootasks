from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from .models import AccountEntity, OwnerTrustedDevice
from .owner_devices import bind_owner_device, revoke_owner_device


@override_settings(OWNER_USERNAME="owner-test")
class OwnerTrustedDeviceTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user(
            username="owner-test",
            password="Strong-Test-Password-123!",
            is_staff=True,
            is_superuser=True,
        )
        self.entity = AccountEntity.objects.create(
            user=self.owner,
            entity_type=AccountEntity.EntityType.OWNER,
            identity_email="owner@example.com",
        )

    def test_maximum_three_active_devices(self):
        for i in range(3):
            bind_owner_device(self.owner, f"device-{i}", f"Device {i}")
        self.assertEqual(
            OwnerTrustedDevice.objects.filter(
                owner_entity=self.entity,
                status=OwnerTrustedDevice.Status.ACTIVE,
            ).count(),
            3,
        )
        with self.assertRaises(ValidationError):
            bind_owner_device(self.owner, "device-4")

    def test_raw_identifier_is_not_stored(self):
        raw = "secret-device-identifier"
        device = bind_owner_device(self.owner, raw)
        self.assertNotEqual(device.device_identifier_hash, raw)
        self.assertEqual(len(device.device_identifier_hash), 64)

    def test_revocation_allows_replacement(self):
        device = bind_owner_device(self.owner, "device-a")
        revoke_owner_device(self.owner, device.pk)
        replacement = bind_owner_device(self.owner, "device-b")
        self.assertEqual(replacement.status, OwnerTrustedDevice.Status.ACTIVE)
        self.assertEqual(
            OwnerTrustedDevice.objects.filter(
                owner_entity=self.entity,
                status=OwnerTrustedDevice.Status.ACTIVE,
            ).count(),
            1,
        )

    def test_non_owner_cannot_bind(self):
        User = get_user_model()
        worker = User.objects.create_user(username="worker")
        with self.assertRaises(PermissionError):
            bind_owner_device(worker, "device-x")
