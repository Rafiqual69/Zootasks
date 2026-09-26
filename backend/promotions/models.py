from django.contrib.auth.models import User
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from accounts.models import AdvertiserProfile


class Promotion(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending Review"),
        ("active", "Active"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("paused", "Paused"),
        ("completed", "Completed"),
        ("expired", "Expired"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    advertiser_name = models.CharField(max_length=150)
    # Nullable for backward compatibility; existing promotions remain valid
    # until a controlled ownership backfill is performed.
    advertiser = models.ForeignKey(
        AdvertiserProfile,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="promotions",
    )
    reward = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    max_workers = models.PositiveIntegerField(default=1)
    completed_workers = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = [
            ("approve_promotion_claim", "Can approve promotion claims"),
            ("reject_promotion_claim", "Can reject promotion claims"),
        ]


    def __str__(self):
        return self.title


class PromotionClaim(models.Model):
    STATUS_CHOICES = [
        ("claimed", "Claimed"),
        ("submitted", "Submitted"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    promotion = models.ForeignKey(
        Promotion,
        on_delete=models.CASCADE,
        related_name="claims",
    )
    worker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="promotion_claims",
    )
    proof = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="claimed",
    )
    claimed_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["promotion", "worker"],
                name="unique_promotion_worker",
            )
        ]

    def __str__(self):
        return f"{self.worker.username} - {self.promotion.title}"



class PromotionFunding(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending Verification"
        VERIFIED = "verified", "Verified"
        RESERVED = "reserved", "Reserved"
        RELEASED = "released", "Released"

    promotion = models.OneToOneField(
        Promotion,
        on_delete=models.PROTECT,
        related_name="funding",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    provider_reference = models.CharField(
        max_length=150,
        unique=True,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    reserved_at = models.DateTimeField(null=True, blank=True)
    released_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        permissions = [
            ("verify_promotion_funding", "Can verify promotion funding"),
            ("reserve_promotion_funding", "Can reserve promotion funding"),
            ("release_promotion_funding", "Can release promotion funding"),
        ]

    def __str__(self):
        return f"{self.promotion.title} - ৳{self.amount} ({self.status})"


class PromotionFundingLedger(models.Model):
    class EntryType(models.TextChoices):
        FUND = "fund", "Funding Received"
        RESERVE = "reserve", "Worker Liability Reserved"
        RELEASE = "release", "Unused Funds Released"
        REFUND = "refund", "Advertiser Refund"

    funding = models.ForeignKey(
        PromotionFunding,
        on_delete=models.PROTECT,
        related_name="ledger_entries",
    )
    entry_type = models.CharField(max_length=20, choices=EntryType.choices)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    idempotency_key = models.CharField(max_length=120, unique=True)
    provider_reference = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self):
        return f"{self.funding_id} - {self.entry_type} - ৳{self.amount}"
