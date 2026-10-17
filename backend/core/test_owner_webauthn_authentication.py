from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone

from .models import OwnerWebAuthnChallenge, OwnerWebAuthnCredential
from .owner_webauthn_authentication import (
    OwnerWebAuthnChallengeDenied,
    consume_owner_authentication_challenge,
    create_owner_authentication_options,
)


@override_settings(
    OWNER_WEBAUTHN_RP_ID="example.com",
    OWNER_WEBAUTHN_ORIGIN="https://example.com",
)
class OwnerWebAuthnAuthenticationChallengeTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(
            username="owner-authentication-challenge-test"
        )
        self.owner_setting = override_settings(OWNER_USER_ID=str(self.owner.pk))
        self.owner_setting.enable()
        self.addCleanup(self.owner_setting.disable)
        self.credential = OwnerWebAuthnCredential.objects.create(
            owner=self.owner,
            device_id="server-generated-device-ref",
            credential_id="AQ",
            public_key=b"public-key-metadata-only",
            sign_count=0,
        )

    def test_options_persist_short_lived_owner_and_rp_bound_challenge(self):
        challenge_id, options_json = create_owner_authentication_options(
            owner_id=self.owner.pk
        )
        row = OwnerWebAuthnChallenge.objects.get(pk=challenge_id)
        self.assertEqual(row.owner_id, self.owner.pk)
        self.assertEqual(row.ceremony, OwnerWebAuthnChallenge.Ceremony.AUTHENTICATION)
        self.assertEqual(row.rp_id, "example.com")
        self.assertEqual(row.origin, "https://example.com")
        self.assertGreater(row.expires_at, timezone.now())
        self.assertIsNone(row.consumed_at)
        self.assertIn("challenge", options_json)

    def test_new_authentication_challenge_invalidates_previous_challenge(self):
        first_id, _ = create_owner_authentication_options(owner_id=self.owner.pk)
        second_id, _ = create_owner_authentication_options(owner_id=self.owner.pk)
        self.assertIsNotNone(
            OwnerWebAuthnChallenge.objects.get(pk=first_id).consumed_at
        )
        self.assertIsNone(
            OwnerWebAuthnChallenge.objects.get(pk=second_id).consumed_at
        )

    def test_challenge_is_consumed_once_and_returns_server_bound_context(self):
        challenge_id, _ = create_owner_authentication_options(owner_id=self.owner.pk)
        result = consume_owner_authentication_challenge(
            owner_id=self.owner.pk,
            challenge_record_id=challenge_id,
        )
        row = OwnerWebAuthnChallenge.objects.get(pk=challenge_id)
        self.assertIsNotNone(row.consumed_at)
        self.assertEqual(result.owner_id, self.owner.pk)
        self.assertEqual(result.challenge, bytes(row.challenge))
        self.assertEqual(result.rp_id, "example.com")
        self.assertEqual(result.origin, "https://example.com")
        with self.assertRaises(OwnerWebAuthnChallengeDenied):
            consume_owner_authentication_challenge(
                owner_id=self.owner.pk,
                challenge_record_id=challenge_id,
            )

    def test_expired_challenge_is_denied(self):
        now = timezone.now()
        challenge_id, _ = create_owner_authentication_options(
            owner_id=self.owner.pk,
            now=now,
        )
        with self.assertRaises(OwnerWebAuthnChallengeDenied):
            consume_owner_authentication_challenge(
                owner_id=self.owner.pk,
                challenge_record_id=challenge_id,
                now=now + timedelta(minutes=5, seconds=1),
            )

    def test_non_owner_cannot_issue_or_consume_challenge(self):
        other = get_user_model().objects.create_user(username="not-configured-owner")
        with self.assertRaises(OwnerWebAuthnChallengeDenied):
            create_owner_authentication_options(owner_id=other.pk)
        challenge_id, _ = create_owner_authentication_options(owner_id=self.owner.pk)
        with self.assertRaises(OwnerWebAuthnChallengeDenied):
            consume_owner_authentication_challenge(
                owner_id=other.pk,
                challenge_record_id=challenge_id,
            )

    def test_missing_rp_configuration_fails_closed(self):
        with override_settings(OWNER_WEBAUTHN_RP_ID="", OWNER_WEBAUTHN_ORIGIN=""):
            with self.assertRaises(OwnerWebAuthnChallengeDenied):
                create_owner_authentication_options(owner_id=self.owner.pk)
