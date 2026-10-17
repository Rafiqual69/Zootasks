from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .adapters import SafeGoogleSocialAccountAdapter
from .models import AccountEntity, WorkerProfile


class GoogleOAuthLoginPageTests(TestCase):
    def test_google_button_is_hidden_when_oauth_is_not_configured(self):
        with override_settings(GOOGLE_OAUTH_ENABLED=False):
            response = self.client.get(reverse("login"), HTTP_HOST="127.0.0.1")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Continue with Google")

    @override_settings(
        GOOGLE_OAUTH_ENABLED=True,
        SOCIALACCOUNT_PROVIDERS={
            "google": {
                "APPS": [
                    {
                        "client_id": "test-client-id",
                        "secret": "test-secret",
                        "key": "",
                    }
                ],
                "SCOPE": ["openid", "profile", "email"],
                "OAUTH_PKCE_ENABLED": True,
            }
        },
    )
    def test_google_button_uses_post_based_provider_login(self):
        response = self.client.get(reverse("login"), HTTP_HOST="127.0.0.1")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Continue with Google")
        self.assertContains(response, 'method="post"')
        self.assertContains(response, "/accounts/google/login/")


class SafeGoogleSocialAccountAdapterTests(TestCase):
    def test_only_google_signup_is_allowed(self):
        adapter = SafeGoogleSocialAccountAdapter()

        self.assertTrue(
            adapter.is_open_for_signup(
                None,
                SimpleNamespace(account=SimpleNamespace(provider="google")),
            )
        )
        self.assertFalse(
            adapter.is_open_for_signup(
                None,
                SimpleNamespace(account=SimpleNamespace(provider="github")),
            )
        )

    def test_social_signup_provisions_worker_not_owner(self):
        user = get_user_model().objects.create_user(
            username="google-worker-test",
            email="google-worker@example.com",
        )
        adapter = SafeGoogleSocialAccountAdapter()

        with patch(
            "allauth.socialaccount.adapter.DefaultSocialAccountAdapter.save_user",
            return_value=user,
        ):
            saved_user = adapter.save_user(
                None,
                SimpleNamespace(account=SimpleNamespace(provider="google")),
            )

        self.assertEqual(saved_user.pk, user.pk)
        self.assertTrue(WorkerProfile.objects.filter(user=user).exists())
        entity = AccountEntity.objects.get(user=user)
        self.assertEqual(entity.entity_type, AccountEntity.EntityType.WORKER)
        self.assertTrue(entity.is_active)
        self.assertFalse(entity.user.is_staff)
        self.assertFalse(entity.user.is_superuser)
