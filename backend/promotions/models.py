from django.contrib.auth.models import User
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


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
