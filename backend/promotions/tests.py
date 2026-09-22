from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Promotion, PromotionClaim


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
