from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.utils import timezone

from .models import (
    AccountEntity,
    OwnerSessionBinding,
    OwnerWebAuthnChallenge,
    OwnerWebAuthnCredential,
)
from .owner_webauthn import (
    complete_owner_webauthn_authentication,
    complete_owner_webauthn_registration,
    issue_owner_webauthn_authentication,
    issue_owner_webauthn_registration,
)


@override_settings(
    OWNER_USERNAME="owner-webauthn-test",
    OWNER_WEBAUTHN_RP_ID="localhost",
    OWNER_WEBAUTHN_ORIGINS=("http://localhost:8000", "http://testserver"),
)
class OwnerWebAuthnTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user(
            username="owner-webauthn-test",
            password="Strong-Test-Password-123!",
            is_staff=True,
            is_superuser=True,
        )
        self.entity = AccountEntity.objects.create(
            user=self.owner,
            entity_type=AccountEntity.EntityType.OWNER,
            identity_email="owner@example.com",
        )
        self.client.force_login(self.owner)
        session = self.client.session
        session["owner_reauthenticated_at"] = timezone.now().timestamp()
        session.save()

    def test_registration_requires_recent_reauthentication(self):
        session = self.client.session
        session.pop("owner_reauthenticated_at", None)
        session.save()
        with self.assertRaises(PermissionError):
            issue_owner_webauthn_registration(self.client.request(), self.owner)

    def test_registration_options_create_short_lived_single_use_challenge(self):
        request = self.client.request()
        request.user = self.owner
        request.session = self.client.session
        options = issue_owner_webauthn_registration(request, self.owner)
        self.assertIn("challenge", options)
        self.assertEqual(
            OwnerWebAuthnChallenge.objects.filter(
                owner_entity=self.entity,
                ceremony=OwnerWebAuthnChallenge.Ceremony.REGISTRATION,
                used_at__isnull=True,
            ).count(),
            1,
        )
        self.assertTrue(request.session.get("owner_webauthn_registration_challenge"))

    @patch("accounts.owner_webauthn.verify_registration_response")
    def test_registration_persists_verified_credential_and_consumes_challenge(
        self, verify
    ):
        request = self.client.request()
        request.user = self.owner
        request.session = self.client.session
        issue_owner_webauthn_registration(request, self.owner)
        challenge = request.session["owner_webauthn_registration_challenge"]
        import base64
        raw_challenge = base64.urlsafe_b64decode(
            challenge + "=" * (-len(challenge) % 4)
        )
        verify.return_value = SimpleNamespace(
            credential_id=b"credential-1",
            credential_public_key=b"public-key-1",
            sign_count=0,
            aaguid="00000000-0000-0000-0000-000000000000",
            credential_device_type=SimpleNamespace(value="single_device"),
            credential_backed_up=False,
        )
        credential = {"id": "credential-1", "rawId": "Y3JlZGVudGlhbC0x"}
        stored = complete_owner_webauthn_registration(
            request, self.owner, credential
        )
        self.assertEqual(stored.credential_id, b"credential-1")
        self.assertEqual(
            OwnerWebAuthnChallenge.objects.filter(
                owner_entity=self.entity,
                challenge_hash__isnull=False,
                used_at__isnull=True,
            ).count(),
            0,
        )
        verify.assert_called_once()
        self.assertEqual(stored.user_handle, self.entity.webauthn_user_handle)
        self.assertTrue(raw_challenge)

    def test_duplicate_registration_is_blocked_by_unique_credential(self):
        OwnerWebAuthnCredential.objects.create(
            owner_entity=self.entity,
            credential_id=b"duplicate",
            public_key=b"public-key",
            user_handle=b"user-handle",
        )
        with self.assertRaises(ValidationError):
            OwnerWebAuthnCredential.objects.create(
                owner_entity=self.entity,
                credential_id=b"duplicate",
                public_key=b"other-key",
                user_handle=b"user-handle",
            )

    def test_authentication_options_require_active_credential(self):
        with self.assertRaises(ValidationError):
            issue_owner_webauthn_authentication(
                self.client.request(), self.owner
            )

    @patch("accounts.owner_webauthn.verify_authentication_response")
    def test_authentication_binds_current_session_server_side(self, verify):
        credential = OwnerWebAuthnCredential.objects.create(
            owner_entity=self.entity,
            credential_id=b"credential-auth",
            public_key=b"public-key-auth",
            user_handle=self.entity.webauthn_user_handle or b"user-handle",
            sign_count=2,
        )
        request = self.client.request()
        request.user = self.owner
        request.session = self.client.session
        issue_owner_webauthn_authentication(request, self.owner)
        verify.return_value = SimpleNamespace(
            credential_id=credential.credential_id,
            new_sign_count=3,
            credential_backed_up=False,
        )
        payload = {
            "id": "Y3JlZGVudGlhbC1hdXRo",
            "rawId": "Y3JlZGVudGlhbC1hdXRo",
            "type": "public-key",
            "response": {},
        }
        bound = complete_owner_webauthn_authentication(
            request, self.owner, payload
        )
        self.assertEqual(bound.pk, credential.pk)
        binding = OwnerSessionBinding.objects.get(
            owner_entity=self.entity,
            revoked_at__isnull=True,
        )
        self.assertEqual(binding.webauthn_credential_id, credential.pk)
        credential.refresh_from_db()
        self.assertEqual(credential.sign_count, 3)
        verify.assert_called_once()

    def test_revoked_credential_cannot_bind(self):
        credential = OwnerWebAuthnCredential.objects.create(
            owner_entity=self.entity,
            credential_id=b"revoked",
            public_key=b"public-key",
            user_handle=self.entity.webauthn_user_handle or b"user-handle",
            revoked_at=timezone.now(),
        )
        request = self.client.request()
        request.user = self.owner
        request.session = self.client.session
        with self.assertRaises(ValidationError):
            issue_owner_webauthn_authentication(request, self.owner)

    def test_non_owner_cannot_issue_options(self):
        User = get_user_model()
        worker = User.objects.create_user(username="webauthn-worker")
        request = self.client.request()
        request.user = worker
        request.session = self.client.session
        with self.assertRaises(PermissionError):
            issue_owner_webauthn_registration(request, worker)

    def test_binding_fails_closed_after_credential_revocation(self):
        credential = OwnerWebAuthnCredential.objects.create(
            owner_entity=self.entity,
            credential_id=b"revoke-after-bind",
            public_key=b"public-key",
            user_handle=self.entity.webauthn_user_handle or b"user-handle",
        )
        binding = OwnerSessionBinding.objects.create(
            owner_entity=self.entity,
            webauthn_credential=credential,
            binding_token_hash="a" * 64,
            session_key_hash="b" * 64,
        )
        self.assertTrue(binding.is_active)
        credential.revoked_at = timezone.now()
        credential.save(update_fields=("revoked_at",))
        binding.refresh_from_db()
        self.assertFalse(binding.is_active)
