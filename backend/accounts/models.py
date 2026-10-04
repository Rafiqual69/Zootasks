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
