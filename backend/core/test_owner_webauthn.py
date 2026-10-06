from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from .models import OwnerWebAuthnCredential
from .owner_webauthn import OwnerWebAuthnDenied, verify_owner_webauthn_assertion


class OwnerWebAuthnBoundaryTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="owner-webauthn-test")

    def test_unknown_credential_is_denied(self):
        with self.assertRaises(OwnerWebAuthnDenied):
            verify_owner_webauthn_assertion(
                owner_id=self.user.pk,
                credential_id="unknown",
                credential={},
                expected_challenge=b"challenge",
                expected_rp_id="example.com",
                expected_origin="https://example.com",
            )

    def test_revoked_credential_is_denied(self):
        OwnerWebAuthnCredential.objects.create(
            owner=self.user,
            device_id="device-1",
            credential_id="AQ",
            public_key=b"not-a-real-key",
            revoked_at=timezone.now() - timedelta(minutes=1),
        )
        with self.assertRaises(OwnerWebAuthnDenied):
            verify_owner_webauthn_assertion(
                owner_id=self.user.pk,
                credential_id="AQ",
                credential={},
                expected_challenge=b"challenge",
                expected_rp_id="example.com",
                expected_origin="https://example.com",
            )

    def test_invalid_challenge_input_is_denied(self):
        with self.assertRaises(OwnerWebAuthnDenied):
            verify_owner_webauthn_assertion(
                owner_id=self.user.pk,
                credential_id="AQ",
                credential={},
                expected_challenge="not-bytes",
                expected_rp_id="example.com",
                expected_origin="https://example.com",
            )
