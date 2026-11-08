from datetime import timedelta

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from .models import WhatsAppOTPChallenge


class WhatsAppOTPChallengeCleanupTests(TestCase):
    def test_cleanup_deletes_only_challenges_older_than_24_hours(self):
        old = WhatsAppOTPChallenge.objects.create(
            phone_number="",
            phone_hash="a" * 64,
            code_hash="b" * 64,
            requester_hash="c" * 64,
            expires_at=timezone.now() - timedelta(days=2),
        )
        recent = WhatsAppOTPChallenge.objects.create(
            phone_number="",
            phone_hash="d" * 64,
            code_hash="e" * 64,
            requester_hash="f" * 64,
            expires_at=timezone.now() + timedelta(minutes=5),
        )
        WhatsAppOTPChallenge.objects.filter(pk=old.pk).update(
            created_at=timezone.now() - timedelta(hours=25)
        )

        call_command("cleanup_whatsapp_otp_challenges")

        self.assertFalse(WhatsAppOTPChallenge.objects.filter(pk=old.pk).exists())
        self.assertTrue(WhatsAppOTPChallenge.objects.filter(pk=recent.pk).exists())
