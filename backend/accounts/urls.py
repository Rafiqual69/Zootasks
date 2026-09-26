from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .forms import OwnerOTPAuthenticationForm
from .views import (
    advertiser_dashboard,
    advertiser_register,
    dashboard,
    owner_email_verification_request,
    owner_email_verify,
    owner_social_oauth_callback,
    owner_social_oauth_start,
    register,
)

urlpatterns = [
    path("owner/login/", LoginView.as_view(
        template_name="accounts/owner_login.html",
        authentication_form=OwnerOTPAuthenticationForm,
        redirect_authenticated_user=False,
    ), name="owner_login"),
    path("owner/email/verify/request/", owner_email_verification_request, name="owner_email_verification_request"),
    path("owner/email/verify/<str:token>/", owner_email_verify, name="owner_email_verify"),
    path("owner/social/<str:provider>/start/", owner_social_oauth_start, name="owner_social_oauth_start"),
    path("owner/social/<str:provider>/callback/", owner_social_oauth_callback, name="owner_social_oauth_callback"),
    path("login/", LoginView.as_view(
        template_name="accounts/login.html",
        redirect_authenticated_user=True,
    ), name="login"),
    path("register/", register, name="register"),
    path("advertiser/register/", advertiser_register, name="advertiser_register"),
    path("advertiser/dashboard/", advertiser_dashboard, name="advertiser_dashboard"),
    path("dashboard/", dashboard, name="dashboard"),
    path("logout/", LogoutView.as_view(next_page="/"), name="logout"),
]
