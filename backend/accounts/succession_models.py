from django.core.exceptions import ValidationError
from django.db import models


class OwnerSuccessionState(models.Model):
    """Explicit, auditable succession state; activation is never automatic."""

    class Status(models.TextChoices):
        OWNER_ACTIVE = "owner_active", "Owner Active"
        ACTIVATION_PENDING = "activation_pending", "Activation Pending"
        SUPER_NOMINEE_ACTIVE = "super_nominee_active", "Super Nominee Active"
        FALLBACK_ACTIVE = "fallback_active", "Fallback Nominee Active"
        SUSPENDED = "suspended", "Suspended"

    owner_entity = models.OneToOneField(
        "accounts.AccountEntity",
        on_delete=models.PROTECT,
        related_name="succession_state",
    )
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.OWNER_ACTIVE,
    )
    activation_reference = models.CharField(max_length=128, blank=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    activated_nominee = models.ForeignKey(
        "accounts.OwnerNominee",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="succession_activations",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if (
            self.owner_entity.entity_type
            != self.owner_entity.EntityType.OWNER
            or not self.owner_entity.is_active
        ):
            raise ValidationError(
                "Succession state requires the canonical active Owner entity."
            )

        if self.status == self.Status.OWNER_ACTIVE and self.activated_nominee_id:
            raise ValidationError(
                "Owner-active state cannot have an activated nominee."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
