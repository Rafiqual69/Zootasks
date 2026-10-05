from django.contrib.auth import get_user_model
from django.db import transaction
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from unittest.mock import patch

from accounts.models import AccountEntity
from .models import Promotion, PromotionClaim


class PromotionXSSTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="xssworker",
            password="testpass123",
        )
        AccountEntity.objects.create(
            user=self.user,
            entity_type=AccountEntity.EntityType.WORKER,
        )
        self.client.login(username="xssworker", password="testpass123")

    def test_non_worker_is_denied_promotion_access(self):
        owner = get_user_model().objects.create_user(
            username="promotion-owner",
            password="testpass123",
        )
        AccountEntity.objects.create(
            user=owner,
            entity_type=AccountEntity.EntityType.OWNER,
        )
        self.client.force_login(owner)

        response = self.client.get(reverse("promotion_marketplace"))

        self.assertEqual(response.status_code, 403)

    def test_marketplace_escapes_untrusted_promotion_content(self):
        Promotion.objects.create(
            title="<script>alert(1)</script>",
            description="<img src=x onerror=\"alert(2)\">",
            advertiser_name="<svg onload=alert(3)>",
            reward="10.00",
            budget="10.00",
            max_workers=5,
            status="active",
        )

        response = self.client.get(reverse("promotion_marketplace"))

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        self.assertNotIn("<script>alert(1)</script>", content)
        self.assertNotIn("<img src=x onerror=\"alert(2)\">", content)
        self.assertNotIn("<svg onload=alert(3)>", content)

        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", content)
        self.assertIn("&lt;img src=x onerror=&quot;alert(2)&quot;&gt;", content)
        self.assertIn("&lt;svg onload=alert(3)&gt;", content)

    def test_submit_page_escapes_untrusted_promotion_content(self):
        promotion = Promotion.objects.create(
            title="<script>alert(4)</script>",
            description="<img src=x onerror=\"alert(5)\">",
            advertiser_name="Safe Advertiser",
            reward="10.00",
            budget="10.00",
            max_workers=5,
            status="active",
        )

        PromotionClaim.objects.create(
            promotion=promotion,
            worker=self.user,
            status="claimed",
        )

        response = self.client.get(
            reverse("submit_promotion", args=[promotion.id])
        )

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        self.assertNotIn("<script>alert(4)</script>", content)
        self.assertNotIn("<img src=x onerror=\"alert(5)\">", content)

        self.assertIn("&lt;script&gt;alert(4)&lt;/script&gt;", content)
        self.assertIn("&lt;img src=x onerror=&quot;alert(5)&quot;&gt;", content)


class PromotionRewardValidationTests(TestCase):
    def test_negative_reward_is_rejected(self):
        from decimal import Decimal
        from django.core.exceptions import ValidationError

        promotion = Promotion(
            title="Test Promotion",
            description="Test",
            advertiser_name="Test Advertiser",
            reward=Decimal("-1.00"),
            budget=Decimal("10.00"),
            max_workers=1,
        )

        with self.assertRaises(ValidationError):
            promotion.full_clean()


class PromotionApprovalNotificationTests(TransactionTestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="notification-worker",
            email="worker@example.com",
        )
        self.promotion = Promotion.objects.create(
            title="Notification Promotion",
            description="Test",
            advertiser_name="Advertiser",
            reward="25.00",
            budget="100.00",
            max_workers=4,
            status="approved",
        )
        self.claim = PromotionClaim.objects.create(
            promotion=self.promotion,
            worker=self.user,
            status="submitted",
        )

    @patch("promotions.signals.send_mail")
    def test_approval_sends_notification_only_after_commit(self, send_mail_mock):
        with transaction.atomic():
            with self.captureOnCommitCallbacks(execute=False) as callbacks:
                self.claim.status = "approved"
                self.claim.save(update_fields=["status"])
            send_mail_mock.assert_not_called()
            self.assertEqual(len(callbacks), 1)

        send_mail_mock.assert_not_called()
        callbacks[0]()
        send_mail_mock.assert_called_once()
        self.assertFalse(send_mail_mock.call_args.kwargs["fail_silently"])

    @patch("promotions.signals.send_mail")
    def test_repeated_approved_save_does_not_duplicate_notification(self, send_mail_mock):
        with transaction.atomic():
            self.claim.status = "approved"
            with self.captureOnCommitCallbacks(execute=True):
                self.claim.save(update_fields=["status"])

        send_mail_mock.assert_called_once()

        with transaction.atomic():
            with self.captureOnCommitCallbacks(execute=True):
                self.claim.save(update_fields=["status"])

        send_mail_mock.assert_called_once()

    @patch("promotions.signals.send_mail")
    def test_notification_failure_is_observable_without_rolling_back(self, send_mail_mock):
        send_mail_mock.side_effect = RuntimeError("smtp unavailable")

        with transaction.atomic():
            self.claim.status = "approved"
            with self.captureOnCommitCallbacks(execute=True):
                self.claim.save(update_fields=["status"])

        self.claim.refresh_from_db()
        self.assertEqual(self.claim.status, "approved")
        send_mail_mock.assert_called_once()
        self.assertFalse(send_mail_mock.call_args.kwargs["fail_silently"])
