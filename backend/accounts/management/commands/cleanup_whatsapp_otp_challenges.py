from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import WhatsAppOTPChallenge


class Command(BaseCommand):
    help = "Delete WhatsApp OTP challenge records older than 24 hours."

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(hours=24)
        deleted, _ = WhatsAppOTPChallenge.objects.filter(
            created_at__lt=cutoff
        ).delete()
        self.stdout.write(
            self.style.SUCCESS(f"Deleted {deleted} expired WhatsApp OTP records.")
        )
