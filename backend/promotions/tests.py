from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .admin import PromotionAdmin, PromotionClaimAdmin
from .models import Promotion, PromotionClaim


class PromotionAdminAuditProtectionTests(TestCase):
    def test_promotion_and_claim_deletion_is_disabled(self):
        promotion_admin = PromotionAdmin(Promotion, admin.site)
        claim_admin = PromotionClaimAdmin(PromotionClaim, admin.site)

        self.assertFalse(promotion_admin.has_delete_permission(None))
        self.assertFalse(claim_admin.has_delete_permission(None))


class PromotionXSSTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="xssworker",
            password="testpass123",
        )
        self.client.login(username="xssworker", password="testpass123")

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


class PromotionAdvertiserOwnershipTests(TestCase):
    def test_promotion_can_reference_advertiser_profile_without_breaking_legacy_field(self):
        from accounts.models import AdvertiserProfile

        advertiser = get_user_model().objects.create_user(
            username="promotion-advertiser",
            password="testpass123",
        )
        profile = AdvertiserProfile.objects.create(
            user=advertiser,
            organization_name="Ownership Co",
            contact_name="Contact",
        )
        promotion = Promotion.objects.create(
            title="Owned Promotion",
            description="Test",
            advertiser_name="Legacy Display Name",
            advertiser=profile,
            reward="10.00",
            budget="20.00",
            max_workers=2,
            status="pending",
        )

        self.assertEqual(promotion.advertiser_id, profile.id)
        self.assertEqual(promotion.advertiser.user_id, advertiser.id)
        self.assertEqual(promotion.advertiser_name, "Legacy Display Name")


class AdvertiserPromotionCreationBoundaryTests(TestCase):
    def setUp(self):
        from accounts.models import AccountEntity, AdvertiserProfile

        self.worker = get_user_model().objects.create_user(
            username="creation-worker",
            password="testpass123",
        )
        self.advertiser = get_user_model().objects.create_user(
            username="creation-advertiser",
            password="testpass123",
        )
        AccountEntity.objects.create(
            user=self.advertiser,
            entity_type=AccountEntity.EntityType.ADVERTISER,
            identity_email="creation@example.com",
        )
        AdvertiserProfile.objects.create(
            user=self.advertiser,
            organization_name="Creation Co",
            contact_name="Owner",
        )

    def test_worker_cannot_create_advertiser_promotion(self):
        self.client.login(username="creation-worker", password="testpass123")
        response = self.client.get(reverse("advertiser_create_promotion"))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Promotion.objects.count(), 0)

    def test_advertiser_creates_pending_owned_promotion(self):
        self.client.login(username="creation-advertiser", password="testpass123")
        response = self.client.post(
            reverse("advertiser_create_promotion"),
            {
                "title": "Safe promotion",
                "description": "A reviewed campaign.",
                "reward": "5.00",
                "budget": "10.00",
                "max_workers": 2,
            },
        )
        self.assertRedirects(response, reverse("advertiser_dashboard"))
        promotion = Promotion.objects.get()
        self.assertEqual(promotion.advertiser.user_id, self.advertiser.id)
        self.assertEqual(promotion.advertiser_name, "Creation Co")
        self.assertEqual(promotion.status, "pending")

    def test_advertiser_cannot_submit_underfunded_promotion(self):
        self.client.login(username="creation-advertiser", password="testpass123")
        response = self.client.post(
            reverse("advertiser_create_promotion"),
            {
                "title": "Underfunded",
                "description": "Insufficient declared budget.",
                "reward": "6.00",
                "budget": "10.00",
                "max_workers": 2,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Promotion.objects.count(), 0)
