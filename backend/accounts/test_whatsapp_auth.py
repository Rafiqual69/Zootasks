from datetime import timedelta
from unittest.mock import patch

from django.db import IntegrityError, transaction

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import (
    AccountEntity,
    WhatsAppIdentity,
    WhatsAppOTPChallenge,
    WorkerProfile,
)
from .whatsapp import keyed_digest, otp_digest


@override_settings(
    WHATSAPP_OTP_ENABLED=True,
    WHATSAPP_OTP_TTL_SECONDS=300,
    WHATSAPP_OTP_RESEND_SECONDS=60,
    WHATSAPP_OTP_MAX_ATTEMPTS=5,
    WHATSAPP_OTP_MAX_SENDS_PER_PHONE_HOUR=5,
    WHATSAPP_OTP_MAX_SENDS_PER_IP_HOUR=10,
    SECRET_KEY="test-only-whatsapp-hmac-secret",
    WHATSAPP_PHONE_HASH_KEY="test-only-stable-phone-hash-key-1234567890",
)
class WhatsAppOTPLoginTests(TestCase):
    phone = "+8801712345678"

    def setUp(self):
        self.client = Client()
        self.phone_hash = keyed_digest("phone:" + self.phone)
        self.send_patcher = patch("accounts.views.send_whatsapp_otp")
        self.send_mock = self.send_patcher.start()
        self.addCleanup(self.send_patcher.stop)
        self.send_mock.return_value = True

    def request_code(self, phone_number="01712345678"):
        response = self.client.post(
            reverse("whatsapp_login"),
            {"action": "send_otp", "phone_number": phone_number},
            HTTP_HOST="testserver",
        )
        return response

    def sent_code(self):
        challenge = WhatsAppOTPChallenge.objects.latest("created_at")
        code = self.send_mock.call_args.args[1]
        self.assertEqual(challenge.phone_number, self.phone)
        self.assertEqual(challenge.code_hash, otp_digest(challenge.pk, code))
        self.assertNotEqual(challenge.code_hash, code)
        return code, challenge

    def verify(self, code):
        return self.client.post(
            reverse("whatsapp_login"),
            {"action": "verify_otp", "code": code},
            HTTP_HOST="testserver",
        )

    def test_local_bangladesh_number_is_normalized_and_worker_is_created(self):
        response = self.request_code()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.send_mock.call_count, 1)

        code, challenge = self.sent_code()
        response = self.verify(code)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("dashboard"))
        identity = WhatsAppIdentity.objects.get(phone_hash=self.phone_hash)
        user = identity.user
        self.assertTrue(user.is_active)
        self.assertTrue(user.has_usable_password() is False)
        self.assertTrue(WorkerProfile.objects.filter(user=user).exists())
        self.assertEqual(
            AccountEntity.objects.get(user=user).entity_type,
            AccountEntity.EntityType.WORKER,
        )
        challenge.refresh_from_db()
        self.assertIsNotNone(challenge.consumed_at)
        self.assertEqual(challenge.phone_number, "")
        self.assertEqual(self.client.session.get("_auth_user_id"), str(user.pk))

    def test_existing_verified_phone_logs_into_same_worker(self):
        user = get_user_model().objects.create_user(
            username="existing-whatsapp-worker",
            password="Strong-Existing-Password-123!",
        )
        WorkerProfile.objects.create(user=user)
        AccountEntity.objects.create(
            user=user,
            entity_type=AccountEntity.EntityType.WORKER,
            is_active=True,
        )
        WhatsAppIdentity.objects.create(
            user=user,
            phone_hash=self.phone_hash,
            phone_last4=self.phone[-4:],
            verified_at=timezone.now(),
        )

        self.request_code()
        code, _ = self.sent_code()
        response = self.verify(code)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session.get("_auth_user_id"), str(user.pk))
        self.assertEqual(WhatsAppIdentity.objects.count(), 1)
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_authenticated_worker_can_link_verified_phone(self):
        user = get_user_model().objects.create_user(
            username="link-worker",
            password="Strong-Link-Password-123!",
        )
        WorkerProfile.objects.create(user=user)
        AccountEntity.objects.create(
            user=user,
            entity_type=AccountEntity.EntityType.WORKER,
            is_active=True,
        )
        self.client.force_login(user)

        self.request_code()
        code, _ = self.sent_code()
        response = self.verify(code)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(WhatsAppIdentity.objects.get().user, user)
        self.assertEqual(self.client.session.get("_auth_user_id"), str(user.pk))

    def test_phone_already_linked_to_other_user_cannot_be_moved(self):
        first = get_user_model().objects.create_user(username="first-linked-worker")
        second = get_user_model().objects.create_user(username="second-linked-worker")
        WorkerProfile.objects.create(user=first)
        WorkerProfile.objects.create(user=second)
        AccountEntity.objects.create(user=first, entity_type=AccountEntity.EntityType.WORKER)
        AccountEntity.objects.create(user=second, entity_type=AccountEntity.EntityType.WORKER)
        WhatsAppIdentity.objects.create(
            user=first,
            phone_hash=self.phone_hash,
            phone_last4=self.phone[-4:],
            verified_at=timezone.now(),
        )
        self.client.force_login(second)

        self.request_code()
        code, _ = self.sent_code()
        response = self.verify(code)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already linked to another account")
        self.assertEqual(WhatsAppIdentity.objects.get().user, first)

    def test_owner_phone_cannot_authenticate_through_whatsapp(self):
        owner = get_user_model().objects.create_user(
            username="protected-owner",
            password="Strong-Owner-Password-123!",
            is_staff=True,
            is_superuser=True,
        )
        AccountEntity.objects.create(
            user=owner,
            entity_type=AccountEntity.EntityType.OWNER,
            is_active=True,
        )
        WhatsAppIdentity.objects.create(
            user=owner,
            phone_hash=self.phone_hash,
            phone_last4=self.phone[-4:],
            verified_at=timezone.now(),
        )

        self.request_code()
        code, _ = self.sent_code()
        response = self.verify(code)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cannot use WhatsApp sign-in")
        self.assertFalse(self.client.session.get("_auth_user_id"))

    def test_invalid_code_is_limited_to_five_attempts(self):
        self.request_code()
        actual_code, challenge = self.sent_code()
        invalid_code = "000000" if actual_code != "000000" else "000001"

        for _ in range(5):
            response = self.verify(invalid_code)
        self.assertEqual(response.status_code, 200)

        challenge.refresh_from_db()
        self.assertEqual(challenge.attempts, 5)
        self.assertIsNotNone(challenge.consumed_at)
        self.assertFalse(self.client.session.get("_auth_user_id"))
        self.assertEqual(WhatsAppIdentity.objects.count(), 0)


    def test_expired_code_is_rejected_and_phone_data_is_cleared(self):
        self.request_code()
        code, challenge = self.sent_code()
        challenge.expires_at = timezone.now() - timedelta(seconds=1)
        challenge.save(update_fields=["expires_at"])

        response = self.verify(code)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(WhatsAppIdentity.objects.count(), 0)
        challenge.refresh_from_db()
        self.assertIsNotNone(challenge.consumed_at)
        self.assertEqual(challenge.phone_number, "")

    def test_database_allows_only_one_active_challenge_per_phone_hash(self):
        first = WhatsAppOTPChallenge.objects.create(
            phone_number=self.phone,
            phone_hash=self.phone_hash,
            code_hash="a" * 64,
            requester_hash=keyed_digest("ip:127.0.0.1"),
            expires_at=timezone.now() + timedelta(minutes=5),
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                WhatsAppOTPChallenge.objects.create(
                    phone_number=self.phone,
                    phone_hash=self.phone_hash,
                    code_hash="b" * 64,
                    requester_hash=keyed_digest("ip:127.0.0.1"),
                    expires_at=timezone.now() + timedelta(minutes=5),
                )
        first.refresh_from_db()
        self.assertIsNone(first.consumed_at)

    def test_resend_cooldown_blocks_second_message(self):
        self.request_code()
        response = self.request_code()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.send_mock.call_count, 1)
        self.assertEqual(WhatsAppOTPChallenge.objects.count(), 1)

    def test_failed_meta_delivery_does_not_create_session_challenge(self):
        from .whatsapp import WhatsAppDeliveryError

        self.send_mock.side_effect = WhatsAppDeliveryError()
        response = self.request_code()

        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.client.session.get("whatsapp_otp_challenge_id"))
        challenge = WhatsAppOTPChallenge.objects.get()
        self.assertIsNotNone(challenge.consumed_at)

    def test_invalid_phone_is_rejected_before_provider_call(self):
        response = self.client.post(
            reverse("whatsapp_login"),
            {"action": "send_otp", "phone_number": "not-a-phone"},
            HTTP_HOST="testserver",
        )

        self.assertEqual(response.status_code, 200)
        self.send_mock.assert_not_called()
        self.assertEqual(WhatsAppOTPChallenge.objects.count(), 0)

    def test_otp_route_loads_and_feature_is_disabled_without_configuration(self):
        with override_settings(WHATSAPP_OTP_ENABLED=False):
            response = self.client.get(reverse("whatsapp_login"), HTTP_HOST="testserver")
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "not active yet")
