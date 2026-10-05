from django.contrib.auth import get_user_model
from django.test import TestCase
from django.contrib import admin
from django.urls import reverse

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


class PromotionAdminAuthorizationTests(TestCase):
    def setUp(self):
        from django.contrib import admin
        from .admin import PromotionAdmin

        self.owner = get_user_model().objects.create_user(
            username="promotion-admin-owner",
            password="StrongTestPass123!",
            is_staff=True,
            is_superuser=True,
        )
        AccountEntity.objects.create(
            user=self.owner,
            entity_type=AccountEntity.EntityType.OWNER,
        )
        self.staff_without_owner = get_user_model().objects.create_user(
            username="promotion-admin-non-owner",
            password="StrongTestPass123!",
            is_staff=True,
            is_superuser=True,
        )
        self.model_admin = PromotionAdmin(Promotion, admin.site)

    def request_for(self, user):
        return type("Request", (), {"user": user})()

    def test_only_active_owner_can_add_change(self):
        self.assertTrue(self.model_admin.has_add_permission(self.request_for(self.owner)))
        self.assertTrue(self.model_admin.has_change_permission(self.request_for(self.owner)))
        self.assertFalse(self.model_admin.has_add_permission(self.request_for(self.staff_without_owner)))
        self.assertFalse(self.model_admin.has_change_permission(self.request_for(self.staff_without_owner)))

    def test_promotion_admin_delete_is_disabled(self):
        self.assertFalse(self.model_admin.has_delete_permission(self.request_for(self.owner)))

    def test_existing_financial_fields_are_readonly(self):
        request = self.request_for(self.owner)
        promotion = Promotion(
            title="Existing",
            description="Existing promotion",
            advertiser_name="Advertiser",
            reward="10.00",
            budget="100.00",
            max_workers=10,
        )
        self.assertEqual(
            set(self.model_admin.get_readonly_fields(request, promotion)),
            {"reward", "budget", "max_workers", "completed_workers"},
        )
        self.assertEqual(self.model_admin.get_readonly_fields(request, None), ())
