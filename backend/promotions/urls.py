from django.urls import path
from .views import advertiser_create_promotion, marketplace, start_promotion, submit_promotion

urlpatterns = [
    path("", marketplace, name="promotion_marketplace"),
    path("advertiser/create/", advertiser_create_promotion, name="advertiser_create_promotion"),
    path("<int:promotion_id>/start/", start_promotion, name="start_promotion"),
    path("<int:promotion_id>/submit/", submit_promotion, name="submit_promotion"),
]
