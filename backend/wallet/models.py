from django.contrib.auth.models import User
from django.db import models


class WalletTransaction(models.Model):
    TRANSACTION_CHOICES = [
        ("earning", "Task Earning"),
        ("withdrawal", "Withdrawal"),
        ("adjustment", "Admin Adjustment"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wallet_transactions")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_CHOICES)
    description = models.CharField(max_length=255)
    task_claim = models.OneToOneField("tasks.TaskClaim", on_delete=models.SET_NULL, null=True, blank=True, related_name="wallet_transaction")
    promotion_claim = models.OneToOneField("promotions.PromotionClaim", on_delete=models.SET_NULL, null=True, blank=True, related_name="wallet_transaction")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - ৳{self.amount}"


class WithdrawalRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("paid", "Paid"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="withdrawal_requests")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    bank_account = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=100)
    account_holder = models.CharField(max_length=150)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-requested_at"]

    def __str__(self):
        return f"{self.user.username} - ৳{self.amount} ({self.status})"
