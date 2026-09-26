from django.contrib import admin

from .models import Offer


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Offers have a reward field but no controlled application workflow yet.
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        # Keep legacy Offer records read-only until a dedicated workflow exists.
        return False

    def has_delete_permission(self, request, obj=None):
        # Preserve offer history; do not delete financial records.
        return False

    readonly_fields = (
        "title",
        "description",
        "partner_name",
        "reward",
        "status",
        "created_at",
    )

    list_display = (
        "title",
        "partner_name",
        "reward",
        "status",
        "created_at",
    )
    list_filter = ("status",)
    search_fields = ("title", "partner_name")
