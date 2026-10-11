from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone

from .models import OwnerWebAuthnChallenge, OwnerWebAuthnCredential
from .owner_webauthn_registration import (
    OwnerWebAuthnRegistrationDenied,
    complete_owner_registration,
    create_owner_registration_options,
)


class OwnerWebAuthnRegistrationTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username="owner-registration-test")
        self.owner_setting = override_settings(OWNER_USER_ID=str(self.owner.pk))
        self.owner_setting.enable()
        self.addCleanup(self.owner_setting.disable)
        self.config = {
            "owner_id": self.owner.pk,
            "rp_id": "example.com",
            "rp_name": "ZooTasks",
            "origin": "https://example.com",
        }

    def test_registration_options_persist_short_lived_challenge(self):
        challenge_id, options_json = create_owner_registration_options(**self.config)
        row = OwnerWebAuthnChallenge.objects.get(pk=challenge_id)
        self.assertEqual(row.owner_id, self.owner.pk)
        self.assertGreater(row.expires_at, timezone.now())
        self.assertIsNone(row.consumed_at)
        self.assertTrue(options_json.startswith("{"))
        self.assertIn("challenge", options_json)

    def test_registration_for_another_account_is_denied(self):
        other = get_user_model().objects.create_user(username="not-the-owner")
        with self.assertRaises(OwnerWebAuthnRegistrationDenied):
            create_owner_registration_options(
                **{**self.config, "owner_id": other.pk},
            )
        self.assertEqual(OwnerWebAuthnChallenge.objects.count(), 0)

    def test_wrong_origin_is_rejected_before_challenge_creation(self):
        with self.assertRaises(OwnerWebAuthnRegistrationDenied):
            create_owner_registration_options(
                **{**self.config, "origin": "https://attacker.example"},
            )
        self.assertEqual(OwnerWebAuthnChallenge.objects.count(), 0)

    @patch("core.owner_webauthn_registration.verify_registration_response")
    def test_successful_verification_stores_only_public_credential_metadata(self, verify):
        challenge_id, _ = create_owner_registration_options(**self.config)
        verify.return_value = SimpleNamespace(
            credential_id=b"credential-id",
            credential_public_key=b"public-key-bytes",
            sign_count=0,
        )
        stored = complete_owner_registration(
            **self.config,
            challenge_record_id=challenge_id,
            credential={"id": "test", "response": {}},
        )
        self.assertEqual(stored.owner_id, self.owner.pk)
        self.assertEqual(stored.public_key, b"public-key-bytes")
        self.assertNotEqual(stored.device_id, "")
        challenge = OwnerWebAuthnChallenge.objects.get(pk=challenge_id)
        self.assertIsNotNone(challenge.consumed_at)
        verify.assert_called_once()

    @patch("core.owner_webauthn_registration.verify_registration_response", side_effect=ValueError("invalid assertion"))
    def test_failed_attempt_consumes_challenge_and_cannot_be_replayed(self, verify):
        challenge_id, _ = create_owner_registration_options(**self.config)
        with self.assertRaises(OwnerWebAuthnRegistrationDenied):
            complete_owner_registration(
                **self.config,
                challenge_record_id=challenge_id,
                credential={"id": "forged"},
            )
        challenge = OwnerWebAuthnChallenge.objects.get(pk=challenge_id)
        self.assertIsNotNone(challenge.consumed_at)
        with self.assertRaises(OwnerWebAuthnRegistrationDenied):
            complete_owner_registration(
                **self.config,
                challenge_record_id=challenge_id,
                credential={"id": "forged"},
            )
        self.assertEqual(OwnerWebAuthnCredential.objects.count(), 0)

    def test_invalid_challenge_record_id_is_rejected(self):
        with self.assertRaises(OwnerWebAuthnRegistrationDenied):
            complete_owner_registration(
                **self.config,
                challenge_record_id="not-a-number",
                credential={"id": "test"},
            )

    def test_expired_challenge_is_rejected(self):
        challenge_id, _ = create_owner_registration_options(**self.config)
        row = OwnerWebAuthnChallenge.objects.get(pk=challenge_id)
        row.expires_at = timezone.now()
        row.save(update_fields=("expires_at",))
        with self.assertRaises(OwnerWebAuthnRegistrationDenied):
            complete_owner_registration(
                **self.config,
                challenge_record_id=challenge_id,
                credential={"id": "test"},
            )
