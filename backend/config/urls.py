from django.contrib import admin
from django.urls import include, path

from core.admin_dashboard import live_wallet_dashboard


urlpatterns = [
    path(
        "admin/live-wallet/",
        admin.site.admin_view(live_wallet_dashboard),
        name="live_wallet_dashboard",
    ),

    path("admin/", admin.site.urls),

    path("accounts/", include("accounts.urls")),
    path("tasks/", include("tasks.urls")),
    path("promotions/", include("promotions.urls")),
    path("wallet/", include("wallet.urls")),

    path("", include("main.urls")),
]
