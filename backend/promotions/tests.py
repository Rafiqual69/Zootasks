from django.contrib.auth import get_user_model
from django.db import transaction
from django.test import TestCase
from decimal import Decimal
from django.urls import reverse
from unittest.mock import patch

from accounts.models import AccountEntity
from .models import Promotion, PromotionClaim
from accounts.models import WorkerProfile
from wallet.models import WalletTransaction


class FinancialAdminHttpTamperingTests(TestCase):
    def setUp(self):
        owner = get_user_model().objects.create_user(
            username="http_promotion_owner",
            password="test-password-123",
            is_staff=True,
            is_superuser=True,
        )
        AccountEntity.objects.create(
            user=owner,
            entity_type=AccountEntity.EntityType.OWNER,
        )
        self.promotion = Promotion.objects.create(
            title="Protected Promotion",
            description="Protected promotion",
            advertiser_name="Test Advertiser",
            reward="15.00",
            budget="100.00",
            max_workers=5,
            reserved_workers=1,
            completed_workers=1,
            status="active",
        )
        self.client.force_login(owner)

    def test_change_post_cannot_tamper_protected_fields(self):
        url = reverse(
            "admin:promotions_promotion_change",
            args=[self.promotion.pk],
        )
        response = self.client.post(
            url,
            {
                "title": "Updated Promotion",
                "description": "Updated description",
                "advertiser_name": "Updated Advertiser",
                "reward": "9999.99",
                "budget": "99999.99",
                "max_workers": "999",
                "completed_workers": "999",
                "status": "completed",
                "_save": "Save",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.promotion.refresh_from_db()
        self.assertEqual(self.promotion.title, "Updated Promotion")
        self.assertEqual(
            self.promotion.description,
            "Updated description",
        )
        self.assertEqual(
            self.promotion.advertiser_name,
            "Updated Advertiser",
        )
        self.assertEqual(self.promotion.reward, Decimal("15.00"))
        self.assertEqual(self.promotion.budget, Decimal("100.00"))
        self.assertEqual(self.promotion.max_workers, 5)
        self.assertEqual(self.promotion.completed_workers, 1)
        self.assertEqual(self.promotion.status, "active")

    def test_owner_can_create_promotion_with_financial_fields(self):
        url = reverse("admin:promotions_promotion_add")
        response = self.client.post(
            url,
            {
                "title": "Owner Created Promotion",
                "description": "Created through authorized admin flow",
                "advertiser_name": "Authorized Advertiser",
                "reward": "20.00",
                "budget": "200.00",
                "max_workers": "4",
                "completed_workers": "0",
                "status": "active",
                "_save": "Save",
            },
        )

        self.assertEqual(response.status_code, 302)
        promotion = Promotion.objects.get(title="Owner Created Promotion")
        self.assertEqual(promotion.reward, Decimal("20.00"))
        self.assertEqual(promotion.budget, Decimal("200.00"))
        self.assertEqual(promotion.max_workers, 4)
        self.assertEqual(promotion.completed_workers, 0)
        self.assertEqual(promotion.status, "active")

    def test_non_owner_cannot_create_promotion(self):
        non_owner = get_user_model().objects.create_user(
            username="http_promotion_add_non_owner",
            password="test-password-123",
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_login(non_owner)

        url = reverse("admin:promotions_promotion_add")
        response = self.client.post(
            url,
            {
                "title": "Unauthorized Created Promotion",
                "description": "Must not be created",
                "advertiser_name": "Unauthorized Advertiser",
                "reward": "9999.99",
                "budget": "99999.99",
                "max_workers": "999",
                "completed_workers": "999",
                "status": "active",
                "_save": "Save",
            },
        )

        self.assertIn(response.status_code, (302, 403))
        self.assertFalse(
            Promotion.objects.filter(
                title="Unauthorized Created Promotion"
            ).exists()
        )


    def test_non_owner_cannot_post_promotion_change(self):
        non_owner = get_user_model().objects.create_user(
            username="http_promotion_non_owner",
            password="test-password-123",
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_login(non_owner)

        url = reverse(
            "admin:promotions_promotion_change",
            args=[self.promotion.pk],
        )
        response = self.client.post(
            url,
            {
                "title": "Unauthorized Promotion Change",
                "description": "Unauthorized",
                "advertiser_name": "Unauthorized Advertiser",
                "reward": "9999.99",
                "budget": "99999.99",
                "max_workers": "999",
                "completed_workers": "999",
                "status": "completed",
                "_save": "Save",
            },
        )

        self.assertIn(response.status_code, (302, 403))
        self.promotion.refresh_from_db()
        self.assertEqual(
            self.promotion.title,
            "Protected Promotion",
        )
        self.assertEqual(self.promotion.reward, Decimal("15.00"))
        self.assertEqual(self.promotion.budget, Decimal("100.00"))
        self.assertEqual(self.promotion.max_workers, 5)
        self.assertEqual(self.promotion.completed_workers, 1)
        self.assertEqual(self.promotion.status, "active")


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


class PromotionApprovalNotificationTests(TestCase):
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


class PromotionAdminWriteBoundaryTests(TestCase):
    def test_promotion_protected_fields_are_read_only(self):
        from django.contrib import admin
        from promotions.admin import PromotionAdmin

        model_admin = PromotionAdmin(Promotion, admin.site)
        self.assertEqual(
            set(model_admin.readonly_fields),
            {"reward", "budget", "max_workers", "reserved_workers", "completed_workers", "status"},
        )


class PromotionClaimAdminReadBoundaryTests(TestCase):
    def test_unprivileged_staff_cannot_view_promotion_claim_admin(self):
        from django.contrib import admin
        from django.test import RequestFactory
        from promotions.admin import PromotionClaimAdmin

        staff = get_user_model().objects.create_user(
            username="limited_promotion_staff",
            password="test-password-123",
            is_staff=True,
        )
        model_admin = PromotionClaimAdmin(PromotionClaim, admin.site)
        request = RequestFactory().get("/admin/promotions/promotionclaim/")
        request.user = staff

        self.assertFalse(model_admin.has_view_permission(request))

    def test_promotion_reviewer_can_view_promotion_claim_admin(self):
        from django.contrib import admin
        from django.contrib.auth.models import Permission
        from django.test import RequestFactory
        from promotions.admin import PromotionClaimAdmin

        reviewer = get_user_model().objects.create_user(
            username="promotion_reviewer",
            password="test-password-123",
            is_staff=True,
        )
        reviewer.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="promotions",
                codename="approve_promotion_claim",
            )
        )
        model_admin = PromotionClaimAdmin(PromotionClaim, admin.site)
        request = RequestFactory().get("/admin/promotions/promotionclaim/")
        request.user = reviewer

        self.assertTrue(model_admin.has_view_permission(request))


class PromotionRewardOperationIntegrityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="promotion_integrity_worker", password="test-password-123")
        AccountEntity.objects.create(user=self.user, entity_type=AccountEntity.EntityType.WORKER)
        WorkerProfile.objects.create(user=self.user, balance=Decimal("100.00"), reserved_balance=Decimal("0.00"), total_earned=Decimal("100.00"))
        self.promotion = Promotion.objects.create(title="Integrity Promotion", description="Test", advertiser_name="Advertiser", reward=Decimal("25.00"), budget=Decimal("100.00"), max_workers=1, status="approved")
        self.claim = PromotionClaim.objects.create(promotion=self.promotion, worker=self.user, status="submitted")

        class ModelAdminStub:
            def message_user(self, request, message, level=None):
                pass
        self.modeladmin = ModelAdminStub()
        self.request = type("RequestStub", (), {})()
        self.request.user = get_user_model().objects.create_superuser(username="promotion_integrity_admin", password="test-admin-password")

    def test_mismatched_existing_payment_does_not_approve_claim(self):
        WalletTransaction.objects.create(user=self.user, amount=Decimal("20.00"), transaction_type="earning", description="Integrity mismatch", promotion_claim=self.claim)
        from promotions.admin import PromotionClaimAdmin
        from django.contrib import admin
        model_admin = PromotionClaimAdmin(PromotionClaim, admin.site)
        from unittest.mock import patch
        with patch.object(model_admin, "message_user"):
            model_admin.approve_claims(self.request, PromotionClaim.objects.filter(pk=self.claim.pk))
        self.claim.refresh_from_db()
        profile = WorkerProfile.objects.get(user=self.user)
        self.assertEqual(self.claim.status, "submitted")
        self.assertEqual(profile.balance, Decimal("100.00"))
        self.assertEqual(profile.total_earned, Decimal("100.00"))


class FinancialAdminPolicyBoundaryTests(TestCase):
    def setUp(self):
        from django.contrib import admin
        from promotions.admin import PromotionAdmin

        self.owner = get_user_model().objects.create_user(
            username="policy_promotion_owner", password="test-password-123",
            is_staff=True, is_superuser=True,
        )
        AccountEntity.objects.create(
            user=self.owner, entity_type=AccountEntity.EntityType.OWNER,
        )
        self.non_owner = get_user_model().objects.create_user(
            username="policy_promotion_non_owner", password="test-password-123",
            is_staff=True, is_superuser=True,
        )
        self.admin = PromotionAdmin(Promotion, admin.site)

    def request_for(self, user):
        return type("Request", (), {"user": user})()

    def test_owner_policy_allows_create_and_change(self):
        request = self.request_for(self.owner)
        self.assertTrue(self.admin.has_add_permission(request))
        promotion = Promotion(
            title="Existing", description="Existing promotion",
            advertiser_name="Advertiser", reward="10.00",
            budget="100.00", max_workers=10,
        )
        self.assertTrue(self.admin.has_change_permission(request, promotion))

    def test_non_owner_is_denied_by_policy(self):
        request = self.request_for(self.non_owner)
        self.assertFalse(self.admin.has_add_permission(request))
        promotion = Promotion(
            title="Existing", description="Existing promotion",
            advertiser_name="Advertiser", reward="10.00",
            budget="100.00", max_workers=10,
        )
        self.assertFalse(self.admin.has_change_permission(request, promotion))

    def test_inactive_owner_entity_is_denied_by_policy(self):
        request = self.request_for(self.owner)
        entity = AccountEntity.objects.get(user=self.owner)
        entity.is_active = False
        entity.save(update_fields=["is_active"])

        promotion = Promotion(
            title="Existing",
            description="Existing promotion",
            advertiser_name="Advertiser",
            reward="10.00",
            budget="100.00",
            max_workers=10,
        )

        self.assertFalse(self.admin.has_add_permission(request))
        self.assertFalse(self.admin.has_change_permission(request, promotion))


    def test_protected_fields_are_immutable_on_existing_objects(self):
        request = self.request_for(self.owner)
        promotion = Promotion(
            title="Existing", description="Existing promotion",
            advertiser_name="Advertiser", reward="10.00",
            budget="100.00", max_workers=10,
        )
        self.assertEqual(
            set(self.admin.get_readonly_fields(request, promotion)),
            {"reward", "budget", "max_workers", "reserved_workers", "completed_workers", "status"},
        )
