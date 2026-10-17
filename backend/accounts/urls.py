from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path

from .views import OwnerLoginView, register, dashboard

urlpatterns = [
    path("owner/login/", OwnerLoginView.as_view(), name="owner_login"),
    path("login/", LoginView.as_view(
        template_name="accounts/login.html",
        redirect_authenticated_user=True
    ), name="login"),
    path("register/", register, name="register"),
    path("dashboard/", dashboard, name="dashboard"),
    path("logout/", LogoutView.as_view(next_page="/"), name="logout"),
    # Keep existing username/password routes above the allauth routes.
    path("", include("allauth.urls")),
]
