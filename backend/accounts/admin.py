from django.contrib import admin

from .models import WorkerProfile


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
