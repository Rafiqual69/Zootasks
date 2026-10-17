"""Core security-control persistence models."""
from django.conf import settings
from django.db import models


class OwnerWebAuthnCredential(models.Model):
    """Public credential metadata for one Owner device.

    Private keys, authenticator secrets, and raw assertions are never stored.
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owner_webauthn_credentials",
    )
    device_id = models.CharField(max_length=128)
    credential_id = models.CharField(max_length=255, unique=True)
    public_key = models.BinaryField()
    sign_count = models.PositiveBigIntegerField(default=0)
    revoked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)


class OwnerWebAuthnChallenge(models.Model):
    """Short-lived, one-time server challenge for WebAuthn registration."""

    class Ceremony(models.TextChoices):
        REGISTRATION = "registration", "Registration"
        AUTHENTICATION = "authentication", "Authentication"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owner_webauthn_challenges",
    )
    challenge = models.BinaryField()
    # Bind the one-time challenge to the exact relying-party configuration used to create it.
    rp_id = models.CharField(max_length=253, null=True, blank=True)
    origin = models.CharField(max_length=512, null=True, blank=True)
    ceremony = models.CharField(
        max_length=24,
        choices=Ceremony.choices,
        default=Ceremony.REGISTRATION,
    )
    expires_at = models.DateTimeField()
    consumed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("owner", "ceremony", "expires_at"), name="core_owner_chal_exp"),
        ]


class OwnerApproval(models.Model):
    """Single-use, server-recorded Owner approval for a bound protected request.

    WebAuthn/passkey verification occurs outside this model. Private keys and
    authenticator secrets are never stored here.
    """

    approval_id = models.UUIDField(unique=True, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owner_approvals",
    )
    device_id = models.CharField(max_length=128)
    credential_id = models.CharField(max_length=255)
    request_digest = models.CharField(max_length=64)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    consumed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)



class OwnerInputRequest(models.Model):
    """Private Owner-submitted command/request; submission never executes it."""

    class Category(models.TextChoices):
        INSTRUCTION = "instruction", "Instruction"
        RESEARCH = "research", "Research request"
        DRAFT = "draft", "Draft/content request"
        CONFIG_PROPOSAL = "config_proposal", "Configuration proposal"
        MONITORING = "monitoring", "Monitoring query"
        PROTECTED_REQUEST = "protected_request", "Protected-action request"

    class Status(models.TextChoices):
        QUEUED = "queued", "Queued for review"
        IN_REVIEW = "in_review", "In review"
        COMPLETED = "completed", "Completed"
        REJECTED = "rejected", "Rejected"

    request_id = models.UUIDField(unique=True, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owner_input_requests",
    )
    category = models.CharField(max_length=32, choices=Category.choices)
    title = models.CharField(max_length=120)
    body = models.TextField(max_length=5000)
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.QUEUED,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("owner", "created_at"), name="core_owner_input_recent"),
            models.Index(fields=("owner", "status"), name="core_owner_input_status"),
        ]

    def __str__(self):
        return f"Owner request {self.request_id} ({self.status})"
