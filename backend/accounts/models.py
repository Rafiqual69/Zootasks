from django.contrib.auth.models import User
from django.db import models


class AccountEntity(models.Model):
    class EntityType(models.TextChoices):
        OWNER = "owner", "Owner"
        SUPER_ADMIN = "super_admin", "Super Admin"
        ADMIN = "admin", "Admin"
        WORKER = "worker", "Worker"
        ADVERTISER = "advertiser", "Advertiser"

    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        related_name="account_entity",
    )
    entity_type = models.CharField(
        max_length=32,
        choices=EntityType.choices,
    )
    identity_email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
    )
    email_verified_at = models.DateTimeField(
        null=True,
        blank=True,
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
                condition=models.Q(entity_type="owner"),
                name="accounts_single_owner_entity",
            ),
        ]

    def __str__(self):
        return f"{self.get_entity_type_display()}: {self.user.username}"


class OwnerIdentityBinding(models.Model):
    account_entity = models.OneToOneField(
        AccountEntity,
        on_delete=models.PROTECT,
        related_name="owner_identity_binding",
    )
    mobile_number = models.CharField(
        max_length=32,
        unique=True,
        null=True,
        blank=True,
    )
    mobile_verified_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    whatsapp_verified_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    telegram_identity = models.OneToOneField(
        "TelegramIdentity",
        on_delete=models.PROTECT,
        related_name="owner_identity_binding",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.account_entity.entity_type != AccountEntity.EntityType.OWNER:
            raise ValidationError(
                "Owner identity binding requires the canonical Owner entity."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Owner identity: {self.account_entity.user.username}"


class AdvertiserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        related_name="advertiser_profile",
    )
    organization_name = models.CharField(max_length=200, blank=True)
    contact_name = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Advertiser Profile"
        verbose_name_plural = "Advertiser Profiles"

    def __str__(self):
        return self.organization_name or self.contact_name or self.user.username


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
