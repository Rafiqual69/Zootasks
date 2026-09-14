from django.contrib import admin
from .models import Offer


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "partner_name",
        "reward",
        "status",
        "created_at",
    )
    list_filter = ("status",)
    search_fields = ("title", "partner_name")
