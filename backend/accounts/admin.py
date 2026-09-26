from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group, User

from .models import AccountEntity, AdvertiserProfile, WorkerProfile


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
