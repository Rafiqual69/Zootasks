from django.urls import path
from .views import marketplace, start_promotion, submit_promotion

urlpatterns = [
    path("", marketplace, name="promotion_marketplace"),
    path("<int:promotion_id>/start/", start_promotion, name="start_promotion"),
    path("<int:promotion_id>/submit/", submit_promotion, name="submit_promotion"),
]
