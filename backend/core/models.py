"""Core security-control persistence models."""
from django.conf import settings
from django.db import models


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
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(device_id=""),
                name="ownerapproval_device_nonempty",
            ),
            models.CheckConstraint(
                condition=~models.Q(credential_id=""),
                name="ownerapproval_credential_nonempty",
            ),
            models.CheckConstraint(
                condition=~models.Q(request_digest=""),
                name="ownerapproval_digest_nonempty",
            ),
        ]
