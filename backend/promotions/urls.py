from django.urls import path

from accounts.authorization import worker_required
from .views import marketplace, start_promotion, submit_promotion

urlpatterns = [
    path("", worker_required(marketplace), name="promotion_marketplace"),
    path(
        "<int:promotion_id>/start/",
        worker_required(start_promotion),
        name="start_promotion",
    ),
    path(
        "<int:promotion_id>/submit/",
        worker_required(submit_promotion),
        name="submit_promotion",
    ),
]
