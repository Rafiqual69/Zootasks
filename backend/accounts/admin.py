from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group, User

from .models import WorkerProfile


# Django's default User/Group admin can mutate privilege-bearing fields.
# Keep those paths locked until ZooTasks has an explicit Owner-controlled
# identity and RBAC management workflow.
admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    def has_add_permission(self, request):
        # Accounts are created through controlled application/identity flows.
        return False

    def has_delete_permission(self, request, obj=None):
        # User deletion can cascade into financial/audit records.
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


@admin.register(WorkerProfile)
class WorkerProfileAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Worker profiles are created by the account/application flow.
        return False

    def has_delete_permission(self, request, obj=None):
        # Profiles contain financial state and must not be deleted from admin.
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
