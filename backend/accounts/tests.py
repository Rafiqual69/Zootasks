from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from .models import AccountEntity
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
        self.assertEqual(response["Location"], "/admin/")
        self.assertEqual(
            self.client.session.get("_auth_user_id"),
            str(self.owner.pk),
        )
        self.assertTrue(self.client.session.get("otp_device_id"))
        self.assertTrue(self.client.session.get("owner_reauthenticated_at"))

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

class AccountEntitySecurityTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="entity_test_user1",
            password="Strong-Test-Password-1",
        )
        self.user2 = User.objects.create_user(
            username="entity_test_user2",
            password="Strong-Test-Password-2",
        )

    def test_account_entity_is_one_to_one_and_protected(self):
        entity = AccountEntity.objects.create(
            user=self.user1,
            entity_type=AccountEntity.EntityType.WORKER,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                AccountEntity.objects.create(
                    user=self.user1,
                    entity_type=AccountEntity.EntityType.WORKER,
                )

        with self.assertRaises(ProtectedError):
            self.user1.delete()

        entity.delete()

    def test_only_one_active_owner_is_allowed(self):
        AccountEntity.objects.create(
            user=self.user1,
            entity_type=AccountEntity.EntityType.OWNER,
            is_active=True,
        )

        with self.assertRaises(IntegrityError):
            AccountEntity.objects.create(
                user=self.user2,
                entity_type=AccountEntity.EntityType.OWNER,
                is_active=True,
            )

    def test_inactive_owner_can_be_historical(self):
        AccountEntity.objects.create(
            user=self.user1,
            entity_type=AccountEntity.EntityType.OWNER,
            is_active=False,
        )

        active_owner = AccountEntity.objects.create(
            user=self.user2,
            entity_type=AccountEntity.EntityType.OWNER,
            is_active=True,
        )

        self.assertTrue(active_owner.is_active)

    def test_multiple_workers_are_allowed_for_different_users(self):
        first = AccountEntity.objects.create(
            user=self.user1,
            entity_type=AccountEntity.EntityType.WORKER,
        )
        second = AccountEntity.objects.create(
            user=self.user2,
            entity_type=AccountEntity.EntityType.WORKER,
        )

        self.assertNotEqual(first.user_id, second.user_id)

    def test_invalid_entity_type_is_rejected_by_model_validation(self):
        entity = AccountEntity(
            user=self.user1,
            entity_type="invalid",
        )

        with self.assertRaises(ValidationError):
            entity.full_clean()


class RegistrationAccountEntityTests(TestCase):
    def test_registration_creates_worker_entity_atomically(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "new-worker",
                "email": "worker@example.com",
                "first_name": "New",
                "last_name": "Worker",
                "password": "Strong-Worker-Password-1",
                "password_confirm": "Strong-Worker-Password-1",
            },
            HTTP_HOST="127.0.0.1",
        )

        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="new-worker")
        entity = AccountEntity.objects.get(user=user)

        self.assertEqual(entity.entity_type, AccountEntity.EntityType.WORKER)
        self.assertTrue(entity.is_active)

    def test_registration_does_not_create_owner_entity(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "normal-user",
                "email": "normal@example.com",
                "first_name": "Normal",
                "last_name": "User",
                "password": "Strong-Normal-Password-1",
                "password_confirm": "Strong-Normal-Password-1",
            },
            HTTP_HOST="127.0.0.1",
        )

        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="normal-user")
        entity = AccountEntity.objects.get(user=user)

        self.assertEqual(entity.entity_type, AccountEntity.EntityType.WORKER)
        self.assertFalse(
            AccountEntity.objects.filter(
                entity_type=AccountEntity.EntityType.OWNER
            ).exists()
        )
