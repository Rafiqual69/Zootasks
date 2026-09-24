from base64 import b32encode

import pyotp
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django_otp.plugins.otp_totp.models import TOTPDevice


@override_settings(OWNER_USERNAME="owner-test")
class OwnerMFATests(TestCase):
    def setUp(self):
        User = get_user_model()

        self.owner = User.objects.create_user(
            username="owner-test",
            password="Strong-Test-Password-123!",
            is_staff=True,
            is_superuser=True,
        )

        self.device = TOTPDevice.objects.create(
            user=self.owner,
            name="owner-primary",
            confirmed=True,
        )

        self.client = Client()

    def current_token(self):
        secret = b32encode(self.device.bin_key).decode("ascii")
        return pyotp.TOTP(secret).now()

    def test_owner_login_with_valid_password_and_totp(self):
        response = self.client.post(
            reverse("owner_login"),
            {
                "username": self.owner.username,
                "password": "Strong-Test-Password-123!",
                "otp_device": self.device.persistent_id,
                "otp_token": self.current_token(),
                "otp_challenge": "",
            },
            HTTP_HOST="127.0.0.1",
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/accounts/dashboard/")
        self.assertEqual(
            self.client.session.get("_auth_user_id"),
            str(self.owner.pk),
        )
        self.assertTrue(self.client.session.get("otp_device_id"))

    def test_owner_login_rejects_wrong_totp(self):
        response = self.client.post(
            reverse("owner_login"),
            {
                "username": self.owner.username,
                "password": "Strong-Test-Password-123!",
                "otp_device": self.device.persistent_id,
                "otp_token": "000000",
                "otp_challenge": "",
            },
            HTTP_HOST="127.0.0.1",
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.client.session.get("_auth_user_id"))
        self.assertContains(response, "Invalid token")

    def test_owner_login_rejects_unconfirmed_mfa(self):
        self.device.confirmed = False
        self.device.save(update_fields=["confirmed"])

        response = self.client.post(
            reverse("owner_login"),
            {
                "username": self.owner.username,
                "password": "Strong-Test-Password-123!",
                "otp_device": self.device.persistent_id,
                "otp_token": "",
                "otp_challenge": "",
            },
            HTTP_HOST="127.0.0.1",
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.client.session.get("_auth_user_id"))
        self.assertContains(response, "MFA is not enrolled")

    def test_owner_login_rejects_non_owner(self):
        User = get_user_model()

        other = User.objects.create_user(
            username="other-user",
            password="Strong-Test-Password-123!",
            is_staff=True,
            is_superuser=True,
        )

        device = TOTPDevice.objects.create(
            user=other,
            name="other-device",
            confirmed=True,
        )

        secret = b32encode(device.bin_key).decode("ascii")
        token = pyotp.TOTP(secret).now()

        response = self.client.post(
            reverse("owner_login"),
            {
                "username": other.username,
                "password": "Strong-Test-Password-123!",
                "otp_device": device.persistent_id,
                "otp_token": token,
                "otp_challenge": "",
            },
            HTTP_HOST="127.0.0.1",
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.client.session.get("_auth_user_id"))
        self.assertContains(
            response,
            "restricted to the Owner account",
        )

    def test_owner_login_page_loads(self):
        response = self.client.get(
            reverse("owner_login"),
            HTTP_HOST="127.0.0.1",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ZooTasks Owner Secure Login")
        self.assertContains(response, "Secure Owner Login")
