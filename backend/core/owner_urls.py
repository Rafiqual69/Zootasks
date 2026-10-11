from django.urls import path

from .owner_console import owner_console

urlpatterns = [
    path("", owner_console, name="owner_console"),
]
