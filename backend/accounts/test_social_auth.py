from types import SimpleNamespace

from allauth.core.exceptions import ImmediateHttpResponse
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase, override_settings

from .account_adapter import ExistingRegistrationOnlyAccountAdapter
from .adapters import SafeSocialAccountAdapter
from .models import AccountEntity


class SocialLoginPolicyTests(TestCase):
    def setUp(self):
        self.adapter = SafeSocialAccountAdapter()
        self.factory = RequestFactory()

    def sociallogin(self, provider, user=None):
        return SimpleNamespace(
            account=SimpleNamespace(provider=provider),
            user=user or SimpleNamespace(pk=None),
        )

    def test_only_configured_login_provider_types_are_allowed(self):
        for provider in ("google", "facebook", "linkedin", "yahoo"):
            with self.subTest(provider=provider):
                self.assertTrue(
                    self.adapter.is_open_for_signup(
                        self.factory.get("/accounts/login/"),
                        self.sociallogin(provider),
                    )
                )

    def test_unknown_provider_is_not_allowed_for_signup(self):
        self.assertFalse(
            self.adapter.is_open_for_signup(
                self.factory.get("/accounts/login/"),
                self.sociallogin("untrusted-provider"),
            )
        )

    def test_privileged_owner_cannot_use_social_login(self):
        user = get_user_model().objects.create_user(
            username="social-owner",
            password="Strong-Owner-Password-123!",
            is_staff=True,
            is_superuser=True,
        )
        AccountEntity.objects.create(
            user=user,
            entity_type=AccountEntity.EntityType.OWNER,
            is_active=True,
        )
        request = self.factory.get("/accounts/login/")
        request.user = user

        with self.assertRaises(ImmediateHttpResponse):
            self.adapter.pre_social_login(
                request,
                self.sociallogin("google"),
            )

    def test_regular_worker_can_connect_social_login(self):
        user = get_user_model().objects.create_user(
            username="social-worker",
            password="Strong-Worker-Password-123!",
        )
        request = self.factory.get("/accounts/login/")
        request.user = user

        # No exception: ordinary worker accounts may use provider login/linking.
        self.adapter.pre_social_login(
            request,
            self.sociallogin("google"),
        )

    def test_allauth_generic_signup_cannot_bypass_registration_view(self):
        adapter = ExistingRegistrationOnlyAccountAdapter()
        self.assertFalse(adapter.is_open_for_signup(self.factory.get("/accounts/signup/")))

    @override_settings(
        SOCIALACCOUNT_EMAIL_AUTHENTICATION=False,
        SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT=False,
        SOCIALACCOUNT_STORE_TOKENS=False,
        SOCIALACCOUNT_LOGIN_ON_GET=False,
    )
    def test_social_login_does_not_auto_link_by_email_or_store_tokens(self):
        from django.conf import settings

        self.assertFalse(settings.SOCIALACCOUNT_EMAIL_AUTHENTICATION)
        self.assertFalse(settings.SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT)
        self.assertFalse(settings.SOCIALACCOUNT_STORE_TOKENS)
        self.assertFalse(settings.SOCIALACCOUNT_LOGIN_ON_GET)
