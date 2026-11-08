import uuid

from django.contrib.auth.models import User
from django.db import models


class WorkerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    skills = models.CharField(max_length=500, blank=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reserved_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_earned = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    completed_tasks = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class TelegramIdentity(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="telegram_identity",
    )
    telegram_user_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=150, blank=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.username:
            return f"@{self.username}"
        return f"Telegram {self.telegram_user_id}"


class AccountEntity(models.Model):
    class EntityType(models.TextChoices):
        OWNER = "owner", "Owner"
        WORKER = "worker", "Worker"

    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        related_name="account_entity",
    )
    entity_type = models.CharField(
        max_length=16,
        choices=EntityType.choices,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Account Entity"
        verbose_name_plural = "Account Entities"
        constraints = [
            models.UniqueConstraint(
                fields=("entity_type",),
                condition=models.Q(entity_type="owner", is_active=True),
                name="accounts_single_owner_entity",
            ),
        ]

    def __str__(self):
        return f"{self.get_entity_type_display()}: {self.user.username}"


class WhatsAppIdentity(models.Model):
    """A phone number becomes an account identifier only after OTP verification."""

    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        related_name="whatsapp_identity",
    )
    phone_hash = models.CharField(max_length=64, unique=True)
    phone_last4 = models.CharField(max_length=4, blank=True)
    verified_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "WhatsApp identity (masked)"


class WhatsAppOTPChallenge(models.Model):
    """Short-lived OTP challenge; only an HMAC of the code is stored."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=16, blank=True, default="")
    phone_hash = models.CharField(max_length=64, db_index=True)
    code_hash = models.CharField(max_length=64)
    requester_hash = models.CharField(max_length=64, db_index=True)
    expires_at = models.DateTimeField(db_index=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    consumed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=("phone_hash", "created_at"), name="accounts_wa_phone_created"),
            models.Index(fields=("requester_hash", "created_at"), name="accounts_wa_ip_created"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=("phone_hash",),
                condition=models.Q(consumed_at__isnull=True),
                name="accounts_one_active_whatsapp_otp",
            ),
        ]

    def __str__(self):
        return "WhatsApp OTP challenge"
