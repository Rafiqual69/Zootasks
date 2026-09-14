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
