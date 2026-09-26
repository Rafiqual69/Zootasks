from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from accounts.email_verification import _hash_token, verify_owner_email_token
from accounts.models import AccountEntity, OwnerEmailVerificationChallenge


class OwnerEmailVerificationTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user(
            username="email-owner",
            password="Strong-Test-Password-123!",
            is_staff=True,
            is_superuser=True,
            email="owner@example.test",
        )
        self.entity = AccountEntity.objects.create(
            user=self.owner,
            entity_type=AccountEntity.EntityType.OWNER,
            identity_email=self.owner.email,
        )
        self.client = Client()

    @patch("accounts.email_verification.send_mail")
    def test_owner_can_request_email_verification(self, send_mail):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("owner_email_verification_request"),
            HTTP_HOST="127.0.0.1",
        )
        self.assertEqual(response.status_code, 200)
        send_mail.assert_called_once()
        challenge = OwnerEmailVerificationChallenge.objects.get(
            account_entity=self.entity
        )
        self.assertGreater(challenge.expires_at, timezone.now())
        self.assertEqual(challenge.attempts, 0)

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="test@example.test",
    )
    def test_owner_email_verification_end_to_end_with_locmem_backend(self):
        self.client.force_login(self.owner)

        request_response = self.client.post(
            reverse("owner_email_verification_request"),
            HTTP_HOST="127.0.0.1",
        )
        self.assertEqual(request_response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)

        message = mail.outbox[0]
        self.assertEqual(message.to, [self.entity.identity_email])
        self.assertIn("ZooTasks Owner email verification", message.subject)

        import re

        match = re.search(
            r"/owner/email/verify/([^/\s]+)",
            message.body,
        )
        self.assertIsNotNone(match)
        token = match.group(1)

        challenge = OwnerEmailVerificationChallenge.objects.get(
            account_entity=self.entity
        )
        self.assertEqual(challenge.attempts, 0)
        self.assertIsNone(challenge.used_at)

        get_response = self.client.get(
            reverse("owner_email_verify", kwargs={"token": token})
        )
        self.assertEqual(get_response.status_code, 200)
        challenge.refresh_from_db()
        self.assertIsNone(challenge.used_at)

        post_response = self.client.post(
            reverse("owner_email_verify", kwargs={"token": token})
        )
        self.assertEqual(post_response.status_code, 200)

        challenge.refresh_from_db()
        self.entity.refresh_from_db()
        self.assertEqual(challenge.attempts, 1)
        self.assertIsNotNone(challenge.used_at)
        self.assertIsNotNone(self.entity.email_verified_at)

        reuse_response = self.client.post(
            reverse("owner_email_verify", kwargs={"token": token})
        )
        self.assertEqual(reuse_response.status_code, 200)
        self.assertIn("invalid", reuse_response.content.decode().lower())

    @patch("accounts.email_verification.send_mail")
    def test_non_owner_cannot_request_email_verification(self, send_mail):
        User = get_user_model()
        worker = User.objects.create_user(
            username="email-worker",
            password="Strong-Test-Password-123!",
            email="worker@example.test",
        )
        AccountEntity.objects.create(
            user=worker,
            entity_type=AccountEntity.EntityType.WORKER,
            identity_email=worker.email,
        )
        self.client.force_login(worker)
        response = self.client.post(
            reverse("owner_email_verification_request"),
            HTTP_HOST="127.0.0.1",
        )
        self.assertEqual(response.status_code, 302)
        send_mail.assert_not_called()

    def test_get_verification_page_does_not_consume_token(self):
        token = "get-only-owner-email-token"
        challenge = OwnerEmailVerificationChallenge.objects.create(
            account_entity=self.entity,
            token_hash=_hash_token(token),
            expires_at=timezone.now() + timedelta(minutes=15),
        )
        response = self.client.get(
            reverse("owner_email_verify", kwargs={"token": token})
        )
        self.assertEqual(response.status_code, 200)
        challenge.refresh_from_db()
        self.assertIsNone(challenge.used_at)
        self.assertIsNone(self.entity.email_verified_at)
        self.assertEqual(response["Referrer-Policy"], "no-referrer")
        self.assertEqual(response["Cache-Control"], "no-store")

    def test_post_verification_consumes_token(self):
        token = "post-owner-email-token"
        challenge = OwnerEmailVerificationChallenge.objects.create(
            account_entity=self.entity,
            token_hash=_hash_token(token),
            expires_at=timezone.now() + timedelta(minutes=15),
        )
        response = self.client.post(
            reverse("owner_email_verify", kwargs={"token": token})
        )
        self.assertEqual(response.status_code, 200)
        challenge.refresh_from_db()
        self.entity.refresh_from_db()
        self.assertIsNotNone(challenge.used_at)
        self.assertIsNotNone(self.entity.email_verified_at)

    def test_owner_email_token_is_single_use(self):
        token = "test-owner-email-token"
        challenge = OwnerEmailVerificationChallenge.objects.create(
            account_entity=self.entity,
            token_hash=_hash_token(token),
            expires_at=timezone.now() + timedelta(minutes=15),
        )
        self.assertTrue(verify_owner_email_token(token))
        self.entity.refresh_from_db()
        challenge.refresh_from_db()
        self.assertIsNotNone(self.entity.email_verified_at)
        self.assertIsNotNone(challenge.used_at)
        self.assertEqual(challenge.attempts, 1)
        self.assertFalse(verify_owner_email_token(token))

    @override_settings(OWNER_EMAIL_VERIFICATION_MAX_ATTEMPTS=2)
    def test_owner_email_token_attempt_limit_is_enforced(self):
        token = "limited-owner-email-token"
        challenge = OwnerEmailVerificationChallenge.objects.create(
            account_entity=self.entity,
            token_hash=_hash_token(token),
            expires_at=timezone.now() + timedelta(minutes=15),
            attempts=2,
        )
        self.assertFalse(verify_owner_email_token(token))
        self.entity.refresh_from_db()
        challenge.refresh_from_db()
        self.assertIsNone(self.entity.email_verified_at)
        self.assertEqual(challenge.attempts, 2)

    def test_owner_email_token_expiry_is_rejected(self):
        token = "expired-owner-email-token"
        OwnerEmailVerificationChallenge.objects.create(
            account_entity=self.entity,
            token_hash=_hash_token(token),
            expires_at=timezone.now() - timedelta(seconds=1),
        )
        self.assertFalse(verify_owner_email_token(token))
        self.entity.refresh_from_db()
        self.assertIsNone(self.entity.email_verified_at)
