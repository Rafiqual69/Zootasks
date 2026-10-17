from datetime import timedelta

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.utils import timezone

from .models import AccountEntity, OwnerSessionBinding, OwnerTrustedDevice
from .owner_devices import (
    approve_owner_device_with_challenge,
    bind_owner_device,
    issue_owner_device_auth_challenge,
    request_owner_device_enrollment,
    verify_owner_device_auth_challenge,
)
from .owner_session_binding import (
    SESSION_BINDING_SESSION_KEY,
    bind_owner_session,
    get_current_owner_session_binding,
    is_owner_session_bound,
    revoke_owner_session_binding,
)


@override_settings(OWNER_USERNAME="owner-session-test")
class OwnerSessionBindingTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user(
            username="owner-session-test",
            password="Strong-Test-Password-123!",
            is_staff=True,
            is_superuser=True,
        )
        self.entity = AccountEntity.objects.create(
            user=self.owner,
            entity_type=AccountEntity.EntityType.OWNER,
            identity_email="owner@example.com",
        )
        self.private_key = Ed25519PrivateKey.generate()
        self.device = bind_owner_device(
            self.owner,
            "session-device-1",
            self.private_key.public_key().public_bytes_raw(),
            "Session Device",
        )
        self.client.force_login(self.owner)

    def test_verified_device_binds_current_owner_session_server_side(self):
        request = self._request()
        binding = bind_owner_session(request, self.owner, self.device.pk)

        self.assertEqual(binding.owner_entity_id, self.entity.pk)
        self.assertEqual(binding.trusted_device_id, self.device.pk)
        self.assertIsNone(binding.revoked_at)

        session = request.session
        token = session.get(SESSION_BINDING_SESSION_KEY)
        self.assertTrue(token)
        self.assertNotEqual(token, str(self.device.pk))
        self.assertNotEqual(token, self.device.device_identifier_hash)
        self.assertTrue(is_owner_session_bound(request))
        self.assertEqual(
            get_current_owner_session_binding(request).pk,
            binding.pk,
        )

    def test_revoked_device_fails_closed_for_existing_bound_session(self):
        request = self._request()
        bind_owner_session(request, self.owner, self.device.pk)

        self.device.status = OwnerTrustedDevice.Status.REVOKED
        self.device.revoked_at = timezone.now()
        self.device.save(update_fields=("status", "revoked_at", "updated_at"))

        self.assertFalse(is_owner_session_bound(request))
        self.assertIsNone(get_current_owner_session_binding(request))

    def test_expired_binding_fails_closed(self):
        request = self._request()
        binding = bind_owner_session(request, self.owner, self.device.pk)
        binding.expires_at = timezone.now() - timedelta(seconds=1)
        binding.save(update_fields=("expires_at",))
        self.assertFalse(is_owner_session_bound(request))

    def test_session_key_change_fails_closed(self):
        request = self._request()
        bind_owner_session(request, self.owner, self.device.pk)
        request.session.cycle_key()

        self.assertFalse(is_owner_session_bound(request))
        self.assertIsNone(get_current_owner_session_binding(request))

    def test_rebinding_same_session_revokes_previous_binding(self):
        request = self._request()
        first = bind_owner_session(request, self.owner, self.device.pk)
        second = bind_owner_session(request, self.owner, self.device.pk)

        first.refresh_from_db()
        self.assertIsNotNone(first.revoked_at)
        self.assertIsNone(second.revoked_at)
        self.assertEqual(
            OwnerSessionBinding.objects.filter(
                owner_entity=self.entity,
                session_key_hash=second.session_key_hash,
                revoked_at__isnull=True,
            ).count(),
            1,
        )

    def test_non_owner_cannot_bind_session(self):
        User = get_user_model()
        worker = User.objects.create_user(
            username="session-worker",
            password="Worker-Password-123!",
        )
        request = self._request(user=worker)

        with self.assertRaises(PermissionError):
            bind_owner_session(request, worker, self.device.pk)

    def test_revocation_clears_current_session_reference(self):
        request = self._request()
        bind_owner_session(request, self.owner, self.device.pk)

        revoke_owner_session_binding(request)

        self.assertIsNone(request.session.get(SESSION_BINDING_SESSION_KEY))
        self.assertFalse(is_owner_session_bound(request))

    def test_invalid_enrollment_signature_is_rejected_and_challenge_remains_pending(self):
        pending_private_key = Ed25519PrivateKey.generate()
        pending_device, challenge = request_owner_device_enrollment(
            self.owner,
            "pending-device-1",
            pending_private_key.public_key().public_bytes_raw(),
            "Pending Device",
        )

        with self.assertRaises(ValidationError):
            approve_owner_device_with_challenge(
                self.owner,
                pending_device.pk,
                challenge,
                b"\x00" * 64,
            )

        pending_device.refresh_from_db()
        self.assertEqual(pending_device.status, OwnerTrustedDevice.Status.PENDING)
        self.assertTrue(pending_device.enrollment_challenge_hash)

        approved = approve_owner_device_with_challenge(
            self.owner,
            pending_device.pk,
            challenge,
            pending_private_key.sign(challenge),
        )
        self.assertEqual(approved.status, OwnerTrustedDevice.Status.ACTIVE)
        self.assertIsNone(approved.enrollment_challenge_hash)

    def test_invalid_auth_signature_is_rejected_and_valid_challenge_is_one_time(self):
        challenge = issue_owner_device_auth_challenge(self.owner, self.device.pk)
        unrelated_private_key = Ed25519PrivateKey.generate()

        with self.assertRaises(ValidationError):
            verify_owner_device_auth_challenge(
                self.owner,
                self.device.pk,
                challenge,
                unrelated_private_key.sign(challenge),
            )

        self.device.refresh_from_db()
        self.assertTrue(self.device.auth_challenge_hash)
        self.assertIsNotNone(self.device.auth_challenge_expires_at)

        verified = verify_owner_device_auth_challenge(
            self.owner,
            self.device.pk,
            challenge,
            self.private_key.sign(challenge),
        )
        self.assertEqual(verified.pk, self.device.pk)
        self.assertIsNone(verified.auth_challenge_hash)
        self.assertIsNone(verified.auth_challenge_expires_at)

        with self.assertRaises(ValidationError):
            verify_owner_device_auth_challenge(
                self.owner,
                self.device.pk,
                challenge,
                self.private_key.sign(challenge),
            )

    def _request(self, user=None):
        request = self.client.request()
        request.user = user or self.owner
        request.session = self.client.session
        return request
