from django.contrib.auth.views import LoginView, LogoutView
from .forms import OwnerOTPAuthenticationForm
from django.urls import path
from .views import advertiser_register, dashboard, register

urlpatterns = [
    path("owner/login/", LoginView.as_view(
        template_name="accounts/owner_login.html",
        authentication_form=OwnerOTPAuthenticationForm,
        redirect_authenticated_user=False,
    ), name="owner_login"),

    path("login/", LoginView.as_view(
        template_name="accounts/login.html",
        redirect_authenticated_user=True
    ), name="login"),
    path("register/", register, name="register"),
    path("advertiser/register/", advertiser_register, name="advertiser_register"),
    path("advertiser/register/", advertiser_register, name="advertiser_register"),
    path("dashboard/", dashboard, name="dashboard"),
    path("logout/", LogoutView.as_view(next_page="/"), name="logout"),
]
