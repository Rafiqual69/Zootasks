from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from .models import AccountEntity, OwnerTrustedDevice
from .owner_devices import (
    approve_owner_device_with_challenge,
    bind_owner_device,
    request_owner_device_enrollment,
    revoke_owner_device,
)


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

    def _keypair(self):
        private_key = Ed25519PrivateKey.generate()
        return private_key, private_key.public_key().public_bytes_raw()

    def test_maximum_three_active_devices(self):
        for i in range(3):
            _, public_key = self._keypair()
            bind_owner_device(self.owner, f"device-{i}", public_key, f"Device {i}")
        self.assertEqual(
            OwnerTrustedDevice.objects.filter(
                owner_entity=self.entity,
                status=OwnerTrustedDevice.Status.ACTIVE,
            ).count(),
            3,
        )
        _, public_key = self._keypair()
        with self.assertRaises(ValidationError):
            bind_owner_device(self.owner, "device-4", public_key)

    def test_raw_identifier_is_not_stored(self):
        raw = "secret-device-identifier"
        _, public_key = self._keypair()
        device = bind_owner_device(self.owner, raw, public_key)
        self.assertNotEqual(device.device_identifier_hash, raw)
        self.assertEqual(len(device.device_identifier_hash), 64)
        self.assertEqual(len(device.public_key), 32)

    def test_pending_enrollment_requires_signature_and_becomes_active(self):
        private_key, public_key = self._keypair()
        device, challenge = request_owner_device_enrollment(
            self.owner, "device-pending", public_key, "Pending device"
        )
        self.assertEqual(device.status, OwnerTrustedDevice.Status.PENDING)

        signature = private_key.sign(challenge)
        activated = approve_owner_device_with_challenge(
            self.owner, device.pk, challenge, signature
        )
        self.assertEqual(activated.status, OwnerTrustedDevice.Status.ACTIVE)
        self.assertIsNone(activated.enrollment_challenge_hash)

    def test_replayed_challenge_is_rejected(self):
        private_key, public_key = self._keypair()
        device, challenge = request_owner_device_enrollment(
            self.owner, "device-replay", public_key
        )
        signature = private_key.sign(challenge)
        approve_owner_device_with_challenge(
            self.owner, device.pk, challenge, signature
        )
        with self.assertRaises(ValidationError):
            approve_owner_device_with_challenge(
                self.owner, device.pk, challenge, signature
            )

    def test_revocation_allows_replacement(self):
        _, public_key = self._keypair()
        device = bind_owner_device(self.owner, "device-a", public_key)
        revoke_owner_device(self.owner, device.pk)
        _, replacement_key = self._keypair()
        replacement = bind_owner_device(self.owner, "device-b", replacement_key)
        self.assertEqual(replacement.status, OwnerTrustedDevice.Status.ACTIVE)

    def test_non_owner_cannot_bind(self):
        User = get_user_model()
        worker = User.objects.create_user(username="worker")
        _, public_key = self._keypair()
        with self.assertRaises(PermissionError):
            bind_owner_device(worker, "device-x", public_key)
