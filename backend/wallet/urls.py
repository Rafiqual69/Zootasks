from django.urls import path

from .views import (
    wallet,
    request_withdrawal,
    withdrawal_success,
    withdrawal_history,
)

urlpatterns = [
    path("", wallet, name="wallet"),

    path(
        "withdraw/",
        request_withdrawal,
        name="request_withdrawal",
    ),

    path(
        "withdraw/success/",
        withdrawal_success,
        name="withdrawal_success",
    ),

    path(
        "withdraw/history/",
        withdrawal_history,
        name="withdrawal_history",
    ),
]
