from django.contrib import admin

from .models import WorkerProfile


@admin.register(WorkerProfile)
class WorkerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "balance",
        "total_earned",
        "completed_tasks",
        "created_at",
    )
    search_fields = ("user__username", "user__email")
    list_filter = ("created_at",)
    # Wallet/earning state must never be directly editable through generic admin forms.
    readonly_fields = ("user", "balance", "reserved_balance", "total_earned", "completed_tasks", "created_at")
