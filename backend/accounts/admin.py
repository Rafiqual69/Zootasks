from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group, User

from .models import (
    AccountEntity,
    AdvertiserProfile,
    OwnerSocialIdentity,
    WorkerProfile,
    OwnerNominee,
    OwnerSuccessionState,
    OwnerWebAuthnCredential,
    OwnerWebAuthnChallenge,
    OwnerSessionBinding,
)


# Django's default User/Group admin can mutate privilege-bearing fields.
# Keep those paths locked until ZooTasks has an explicit Owner-controlled
# identity and RBAC management workflow.
admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(AccountEntity)
class AccountEntityAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Entity provisioning will use a dedicated Owner-controlled flow.
        return False

    def has_change_permission(self, request, obj=None):
        # Entity type and identity binding are security-sensitive.
        return False

    def has_delete_permission(self, request, obj=None):
        # Identity records must remain available for audit/recovery history.
        return False

    list_display = (
        "user",
        "entity_type",
        "identity_email",
        "email_verified_at",
        "is_active",
        "created_at",
    )
    list_filter = ("entity_type", "is_active")
    search_fields = ("user__username", "identity_email")
    readonly_fields = (
        "user",
        "entity_type",
        "identity_email",
        "email_verified_at",
        "is_active",
        "created_at",
        "updated_at",
    )


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    readonly_fields = (
        "is_staff",
        "is_superuser",
        "groups",
        "user_permissions",
        "last_login",
        "date_joined",
    )


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = ("name",)
    search_fields = ("name",)
    readonly_fields = ("name", "permissions")


@admin.register(AdvertiserProfile)
class AdvertiserProfileAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = (
        "user",
        "organization_name",
        "contact_name",
        "created_at",
    )
    search_fields = (
        "user__username",
        "user__email",
        "organization_name",
        "contact_name",
    )
    readonly_fields = (
        "user",
        "organization_name",
        "contact_name",
        "created_at",
        "updated_at",
    )


@admin.register(WorkerProfile)
class WorkerProfileAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = (
        "user",
        "balance",
        "reserved_balance",
        "total_earned",
        "completed_tasks",
        "created_at",
    )
    search_fields = ("user__username", "user__email")
    list_filter = ("created_at",)

    readonly_fields = (
        "user",
        "balance",
        "reserved_balance",
        "total_earned",
        "completed_tasks",
        "created_at",
    )


@admin.register(OwnerSocialIdentity)
class OwnerSocialIdentityAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = (
        "account_entity",
        "provider",
        "provider_user_id",
        "username",
        "verified_at",
        "created_at",
    )
    list_filter = ("provider", "verified_at")
    search_fields = ("account_entity__user__username", "provider_user_id", "username")
    readonly_fields = (
        "account_entity",
        "provider",
        "provider_user_id",
        "username",
        "verified_at",
        "created_at",
        "updated_at",
    )


@admin.register(OwnerNominee)
class OwnerNomineeAdmin(admin.ModelAdmin):
    """Read-only audit surface; appointment/revocation stays Owner-workflow controlled."""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = (
        "owner_entity",
        "nominee_user",
        "role",
        "succession_order",
        "is_active",
        "appointed_at",
        "revoked_at",
    )
    list_filter = ("role", "is_active")
    search_fields = ("owner_entity__user__username", "nominee_user__username")
    readonly_fields = (
        "owner_entity", "nominee_user", "role", "succession_order",
        "is_active", "appointed_at", "updated_at", "revoked_at",
    )


@admin.register(OwnerSuccessionState)
class OwnerSuccessionStateAdmin(admin.ModelAdmin):
    """Read-only audit surface; succession activation requires a dedicated gate."""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = (
        "owner_entity",
        "status",
        "activated_nominee",
        "activation_reference",
        "activated_at",
        "updated_at",
    )
    list_filter = ("status",)
    search_fields = ("owner_entity__user__username", "activation_reference")
    readonly_fields = (
        "owner_entity", "status", "activation_reference",
        "activated_at", "activated_nominee", "created_at", "updated_at",
    )


@admin.register(OwnerWebAuthnCredential)
class OwnerWebAuthnCredentialAdmin(admin.ModelAdmin):
    """Read-only WebAuthn credential audit surface."""
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = (
        "owner_entity",
        "label",
        "aaguid",
        "sign_count",
        "backup_eligible",
        "backed_up",
        "created_at",
        "last_used_at",
        "revoked_at",
    )
    list_filter = ("backup_eligible", "backed_up", "revoked_at")
    search_fields = ("owner_entity__user__username", "label", "aaguid")
    readonly_fields = (
        "owner_entity",
        "credential_id",
        "public_key",
        "user_handle",
        "sign_count",
        "aaguid",
        "transports",
        "label",
        "backup_eligible",
        "backed_up",
        "created_at",
        "last_used_at",
        "revoked_at",
    )


@admin.register(OwnerWebAuthnChallenge)
class OwnerWebAuthnChallengeAdmin(admin.ModelAdmin):
    """Read-only challenge audit surface; raw challenges are never stored."""
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = (
        "owner_entity",
        "ceremony",
        "expires_at",
        "used_at",
        "created_at",
    )
    list_filter = ("ceremony", "used_at")
    search_fields = ("owner_entity__user__username", "session_key_hash")
    readonly_fields = (
        "owner_entity",
        "session_key_hash",
        "ceremony",
        "challenge_hash",
        "expires_at",
        "used_at",
        "created_at",
    )


@admin.register(OwnerSessionBinding)
class OwnerSessionBindingAdmin(admin.ModelAdmin):
    """Read-only server-side Owner session binding audit surface."""
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = (
        "owner_entity",
        "trusted_device",
        "webauthn_credential",
        "created_at",
        "last_seen_at",
        "revoked_at",
    )
    list_filter = ("revoked_at",)
    search_fields = ("owner_entity__user__username", "session_key_hash")
    readonly_fields = (
        "owner_entity",
        "trusted_device",
        "webauthn_credential",
        "binding_token_hash",
        "session_key_hash",
        "created_at",
        "last_seen_at",
        "revoked_at",
    )
