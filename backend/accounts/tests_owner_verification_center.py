from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import AccountEntity


class OwnerVerificationCenterActionTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner-verification-ui",
            password="Strong-Test-Password-123!",
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )
        self.entity = AccountEntity.objects.create(
            user=self.owner,
            entity_type=AccountEntity.EntityType.OWNER,
            identity_email="owner-ui@example.test",
        )

    @patch("accounts.email_verification.send_mail")
    def test_owner_can_request_email_from_verification_center(self, send_mail):
        self.client.force_login(self.owner)
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                reverse("owner_email_verification_request"),
                HTTP_HOST="127.0.0.1",
            )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["Location"],
            reverse("owner_verification_center"),
        )
        send_mail.assert_called_once()

    def test_non_owner_cannot_request_email_verification(self):
        worker = User.objects.create_user(
            username="worker-verification-ui",
            password="Strong-Test-Password-123!",
            is_active=True,
        )
        AccountEntity.objects.create(
            user=worker,
            entity_type=AccountEntity.EntityType.WORKER,
            identity_email="worker-ui@example.test",
        )
        self.client.force_login(worker)
        response = self.client.post(
            reverse("owner_email_verification_request"),
            HTTP_HOST="127.0.0.1",
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("login"))

    def test_verified_email_hides_request_form(self):
        self.entity.email_verified_at = __import__("django.utils.timezone", fromlist=["timezone"]).timezone.now()
        self.entity.save(update_fields=["email_verified_at"])
        self.client.force_login(self.owner)
        response = self.client.get(
            reverse("owner_verification_center"),
            HTTP_HOST="127.0.0.1",
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Send verification email")
