from django.conf import settings
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
    entity_type = models.CharField(max_length=32, choices=EntityType.choices)
    identity_email = models.EmailField(unique=True, null=True, blank=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    webauthn_user_handle = models.BinaryField(max_length=64, unique=True, null=True, blank=True)
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
    account_entity = models.OneToOneField(AccountEntity, on_delete=models.PROTECT, related_name="owner_identity_binding")
    mobile_number = models.CharField(max_length=32, unique=True, null=True, blank=True)
    mobile_verified_at = models.DateTimeField(null=True, blank=True)
    whatsapp_verified_at = models.DateTimeField(null=True, blank=True)
    telegram_identity = models.OneToOneField("TelegramIdentity", on_delete=models.PROTECT, related_name="owner_identity_binding", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.account_entity.entity_type != AccountEntity.EntityType.OWNER or not self.account_entity.is_active:
            raise ValidationError("Owner identity binding requires the canonical active Owner entity.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Owner identity: {self.account_entity.user.username}"


class OwnerSocialIdentity(models.Model):
    class Provider(models.TextChoices):
        FACEBOOK = "facebook", "Facebook"
        INSTAGRAM = "instagram", "Instagram"

    account_entity = models.ForeignKey(AccountEntity, on_delete=models.PROTECT, related_name="owner_social_identities")
    provider = models.CharField(max_length=32, choices=Provider.choices)
    provider_user_id = models.CharField(max_length=255)
    username = models.CharField(max_length=150, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("provider", "provider_user_id"), name="accounts_unique_owner_social_identity"),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.account_entity.entity_type != AccountEntity.EntityType.OWNER or not self.account_entity.is_active:
            raise ValidationError("Owner social identity requires the canonical active Owner entity.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_provider_display()} identity"


class OwnerEmailVerificationChallenge(models.Model):
    account_entity = models.ForeignKey(AccountEntity, on_delete=models.PROTECT, related_name="owner_email_verification_challenges")
    token_hash = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.account_entity.entity_type != AccountEntity.EntityType.OWNER or not self.account_entity.is_active:
            raise ValidationError("Owner email verification requires the canonical active Owner entity.")

    def is_valid(self, now=None):
        from django.utils import timezone
        now = now or timezone.now()
        max_attempts = getattr(settings, "OWNER_EMAIL_VERIFICATION_MAX_ATTEMPTS", 5)
        return self.used_at is None and self.expires_at > now and self.attempts < max_attempts

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Owner email verification: {self.account_entity.user.username}"


class OwnerSocialOAuthState(models.Model):
    account_entity = models.ForeignKey(AccountEntity, on_delete=models.PROTECT, related_name="owner_social_oauth_states")
    provider = models.CharField(max_length=32, choices=OwnerSocialIdentity.Provider.choices)
    state_hash = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=("account_entity", "provider", "created_at"), name="accounts_social_oauth_idx"),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.account_entity.entity_type != AccountEntity.EntityType.OWNER or not self.account_entity.is_active:
            raise ValidationError("Owner social OAuth state requires the canonical active Owner entity.")

    def is_valid(self, now=None):
        from django.utils import timezone
        now = now or timezone.now()
        return self.used_at is None and self.expires_at > now

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class OwnerNominee(models.Model):
    """Owner-controlled succession nominee; financial authority is intentionally separate."""

    class Role(models.TextChoices):
        SUPER_NOMINEE = "super_nominee", "Super Nominee"
        NOMINEE = "nominee", "Nominee"

    owner_entity = models.ForeignKey(AccountEntity, on_delete=models.PROTECT, related_name="owner_nominees")
    nominee_user = models.OneToOneField(User, on_delete=models.PROTECT, related_name="owner_nomination")
    role = models.CharField(max_length=32, choices=Role.choices, default=Role.NOMINEE)
    succession_order = models.PositiveSmallIntegerField()
    is_active = models.BooleanField(default=True)
    appointed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("succession_order", "appointed_at")
        constraints = [
            models.UniqueConstraint(
                fields=("owner_entity", "succession_order"),
                condition=models.Q(is_active=True),
                name="accounts_unique_active_nominee_succession_order",
            ),
            models.UniqueConstraint(
                fields=("owner_entity",),
                condition=models.Q(role="super_nominee", is_active=True),
                name="accounts_single_active_super_nominee",
            ),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.owner_entity.entity_type != AccountEntity.EntityType.OWNER or not self.owner_entity.is_active:
            raise ValidationError("Nominees require the canonical active Owner entity.")
        if self.nominee_user_id == self.owner_entity.user_id:
            raise ValidationError("The Owner cannot be appointed as a nominee.")
        if not 1 <= self.succession_order <= 6:
            raise ValidationError("Nominee succession order must be between 1 and 6.")
        if self.revoked_at and self.is_active:
            raise ValidationError("A revoked nominee cannot remain active.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_role_display()}: {self.nominee_user.username}"


class OwnerSuccessionState(models.Model):
    """Extension point for verified succession; activation remains explicitly gated."""

    class Status(models.TextChoices):
        OWNER_ACTIVE = "owner_active", "Owner Active"
        ACTIVATION_PENDING = "activation_pending", "Activation Pending"
        SUPER_NOMINEE_ACTIVE = "super_nominee_active", "Super Nominee Active"
        FALLBACK_ACTIVE = "fallback_active", "Fallback Nominee Active"
        SUSPENDED = "suspended", "Suspended"

    owner_entity = models.OneToOneField(AccountEntity, on_delete=models.PROTECT, related_name="succession_state")
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.OWNER_ACTIVE)
    activation_reference = models.CharField(max_length=128, blank=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    activated_nominee = models.ForeignKey(OwnerNominee, on_delete=models.PROTECT, null=True, blank=True, related_name="succession_activations")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.owner_entity.entity_type != AccountEntity.EntityType.OWNER or not self.owner_entity.is_active:
            raise ValidationError("Succession state requires the canonical active Owner entity.")
        if self.status == self.Status.OWNER_ACTIVE and self.activated_nominee_id:
            raise ValidationError("Owner-active state cannot have an activated nominee.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class OwnerTrustedDevice(models.Model):
    """Server-side trusted device binding; raw device identifiers are never stored."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACTIVE = "active", "Active"
        REVOKED = "revoked", "Revoked"

    owner_entity = models.ForeignKey(
        AccountEntity,
        on_delete=models.PROTECT,
        related_name="trusted_devices",
    )
    device_identifier_hash = models.CharField(max_length=64)
    public_key = models.BinaryField(max_length=32, null=True, blank=True)
    enrollment_challenge_hash = models.CharField(max_length=64, null=True, blank=True)
    enrollment_challenge_expires_at = models.DateTimeField(null=True, blank=True)
    auth_challenge_hash = models.CharField(max_length=64, null=True, blank=True)
    auth_challenge_expires_at = models.DateTimeField(null=True, blank=True)
    label = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    approved_at = models.DateTimeField(null=True, blank=True)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("owner_entity", "device_identifier_hash"),
                condition=models.Q(status="active"),
                name="accounts_unique_active_owner_device",
            ),
        ]
        indexes = [
            models.Index(
                fields=("owner_entity", "status"),
                name="acct_owner_dev_status_idx",
            ),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.owner_entity.entity_type != AccountEntity.EntityType.OWNER or not self.owner_entity.is_active:
            raise ValidationError("Trusted device requires the canonical active Owner entity.")
        if self.status == self.Status.REVOKED and not self.revoked_at:
            raise ValidationError("Revoked device must have a revocation timestamp.")
        if self.status == self.Status.ACTIVE and self.revoked_at:
            raise ValidationError("Active device cannot have a revocation timestamp.")
        if self.status == self.Status.ACTIVE and not self.public_key:
            raise ValidationError("Active trusted device requires a public key.")
        if self.status == self.Status.PENDING and not self.enrollment_challenge_hash:
            raise ValidationError("Pending trusted device requires an enrollment challenge.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class OwnerSessionBinding(models.Model):
    """Server-side binding between an authenticated Owner session and a trusted device."""

    owner_entity = models.ForeignKey(
        AccountEntity,
        on_delete=models.PROTECT,
        related_name="owner_session_bindings",
    )
    trusted_device = models.ForeignKey(
        OwnerTrustedDevice,
        on_delete=models.PROTECT,
        related_name="session_bindings",
    )
    binding_token_hash = models.CharField(max_length=64, unique=True)
    session_key_hash = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("owner_entity", "session_key_hash"),
                condition=models.Q(revoked_at__isnull=True),
                name="acct_owner_sess_active_uniq",
            ),
        ]
        indexes = [
            models.Index(
                fields=("owner_entity", "revoked_at"),
                name="acct_owner_sess_rev_idx",
            ),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.owner_entity.entity_type != AccountEntity.EntityType.OWNER or not self.owner_entity.is_active:
            raise ValidationError("Owner session binding requires the canonical active Owner entity.")
        if self.trusted_device.owner_entity_id != self.owner_entity_id:
            raise ValidationError("Trusted device must belong to the same Owner entity.")
        if self.revoked_at is None and self.trusted_device.status != OwnerTrustedDevice.Status.ACTIVE:
            raise ValidationError("Active session binding requires an active trusted device.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.revoked_at is None and self.trusted_device.status == OwnerTrustedDevice.Status.ACTIVE


class OwnerWebAuthnCredential(models.Model):
    """Phishing-resistant WebAuthn credential bound to the canonical Owner."""

    owner_entity = models.ForeignKey(
        AccountEntity,
        on_delete=models.PROTECT,
        related_name="webauthn_credentials",
    )
    credential_id = models.BinaryField(max_length=1024, unique=True)
    public_key = models.BinaryField(max_length=4096)
    user_handle = models.BinaryField(max_length=64)
    sign_count = models.PositiveBigIntegerField(default=0)
    aaguid = models.CharField(max_length=36, blank=True)
    transports = models.JSONField(default=list, blank=True)
    label = models.CharField(max_length=100, blank=True)
    backup_eligible = models.BooleanField(default=False)
    backed_up = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(
                fields=("owner_entity", "revoked_at"),
                name="acct_owner_webauthn_idx",
            ),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError
        if (
            self.owner_entity.entity_type != AccountEntity.EntityType.OWNER
            or not self.owner_entity.is_active
        ):
            raise ValidationError(
                "WebAuthn credentials require the canonical active Owner entity."
            )
        if len(self.user_handle) > 64:
            raise ValidationError("WebAuthn user handle must not exceed 64 bytes.")
        if self.revoked_at is not None and self.last_used_at is not None:
            pass

    @property
    def is_active(self):
        return self.revoked_at is None

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class OwnerWebAuthnChallenge(models.Model):
    """Single-use, short-lived server-side WebAuthn ceremony challenge."""

    class Ceremony(models.TextChoices):
        REGISTRATION = "registration", "Registration"
        AUTHENTICATION = "authentication", "Authentication"

    owner_entity = models.ForeignKey(
        AccountEntity,
        on_delete=models.PROTECT,
        related_name="webauthn_challenges",
    )
    session_key_hash = models.CharField(max_length=64)
    ceremony = models.CharField(max_length=20, choices=Ceremony.choices)
    challenge_hash = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(
                fields=("owner_entity", "ceremony", "created_at"),
                name="acct_owner_webauthn_chal_idx",
            ),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError
        if (
            self.owner_entity.entity_type != AccountEntity.EntityType.OWNER
            or not self.owner_entity.is_active
        ):
            raise ValidationError(
                "WebAuthn challenges require the canonical active Owner entity."
            )

    def is_valid(self, now=None):
        from django.utils import timezone
        now = now or timezone.now()
        return self.used_at is None and self.expires_at > now

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class AdvertiserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name="advertiser_profile")
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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="telegram_identity")
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
