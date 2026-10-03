from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from unittest.mock import patch
from django.urls import reverse

from accounts.models import AccountEntity, OwnerSocialIdentity, OwnerSocialOAuthState


class OwnerSocialOAuthViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="oauth-view-owner",
            password="test-password-123",
        )
        self.owner_entity = AccountEntity.objects.create(
            user=self.owner,
            entity_type=AccountEntity.EntityType.OWNER,
            identity_email="oauth-view-owner@example.test",
        )

    @override_settings(
        OWNER_FACEBOOK_OAUTH_CLIENT_ID="facebook-client",
        OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT="https://www.facebook.com/dialog/oauth",
        OWNER_FACEBOOK_OAUTH_TOKEN_ENDPOINT="https://graph.facebook.com/oauth/access_token",
        OWNER_FACEBOOK_OAUTH_REDIRECT_URI="https://zootasks.example/accounts/owner/social/facebook/callback/",
        OWNER_FACEBOOK_OAUTH_SCOPES="scope_a,scope_b",
    )
    def test_start_issues_state_and_redirects(self):
        self.client.force_login(self.owner)

        response = self.client.get(
            reverse(
                "owner_social_oauth_start",
                kwargs={"provider": OwnerSocialIdentity.Provider.FACEBOOK},
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("state=", response["Location"])
        self.assertEqual(
            OwnerSocialOAuthState.objects.filter(
                account_entity=self.owner_entity,
                provider=OwnerSocialIdentity.Provider.FACEBOOK,
            ).count(),
            1,
        )

    def test_non_owner_cannot_start(self):
        worker = User.objects.create_user(
            username="oauth-view-worker",
            password="test-password-123",
        )
        AccountEntity.objects.create(
            user=worker,
            entity_type=AccountEntity.EntityType.WORKER,
            identity_email="oauth-view-worker@example.test",
        )
        self.client.force_login(worker)

        response = self.client.get(
            reverse(
                "owner_social_oauth_start",
                kwargs={"provider": OwnerSocialIdentity.Provider.FACEBOOK},
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_callback_rejects_missing_parameters(self):
        self.client.force_login(self.owner)

        response = self.client.get(
            reverse(
                "owner_social_oauth_callback",
                kwargs={"provider": OwnerSocialIdentity.Provider.FACEBOOK},
            )
        )

        self.assertEqual(response.status_code, 400)

    @override_settings(
        OWNER_FACEBOOK_OAUTH_CLIENT_ID="facebook-client",
        OWNER_FACEBOOK_OAUTH_CLIENT_SECRET="facebook-secret",
        OWNER_FACEBOOK_OAUTH_TOKEN_ENDPOINT="https://graph.facebook.com/oauth/access_token",
        OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT="https://www.facebook.com/dialog/oauth",
        OWNER_FACEBOOK_OAUTH_REDIRECT_URI="https://zootasks.example/accounts/owner/social/facebook/callback/",
        OWNER_FACEBOOK_OAUTH_SCOPES="scope_a",
        OWNER_FACEBOOK_OAUTH_PROFILE_ENDPOINT="https://graph.facebook.com/me",
        OWNER_FACEBOOK_OAUTH_PROFILE_FIELDS="id,name",
    )
    @patch("accounts.views.bind_verified_owner_social_identity")
    @patch("accounts.views.get_owner_social_profile")
    @patch("accounts.views.exchange_owner_social_authorization_code")
    def test_callback_exchanges_profile_and_binds_identity(
        self,
        mock_exchange,
        mock_profile,
        mock_bind,
    ):
        from accounts.social_oauth_exchange import (
            OwnerSocialOAuthProfile,
            OwnerSocialOAuthTokenResponse,
        )

        self.client.force_login(self.owner)
        state = "callback-success-state"
        OwnerSocialOAuthState.objects.create(
            account_entity=self.owner_entity,
            provider=OwnerSocialIdentity.Provider.FACEBOOK,
            state_hash=__import__("hashlib").sha256(
                state.encode("utf-8")
            ).hexdigest(),
            expires_at=__import__("django.utils.timezone").utils.timezone.now()
            + __import__("datetime").timedelta(minutes=10),
        )
        mock_exchange.return_value = OwnerSocialOAuthTokenResponse(
            access_token="temporary-access-token",
            token_type="Bearer",
            expires_in=3600,
        )
        mock_profile.return_value = OwnerSocialOAuthProfile(
            provider_user_id="facebook-owner-123",
            username="owner",
        )

        response = self.client.get(
            reverse(
                "owner_social_oauth_callback",
                kwargs={"provider": OwnerSocialIdentity.Provider.FACEBOOK},
            ),
            {"state": state, "code": "provider-code"},
        )

        self.assertEqual(response.status_code, 200)
        mock_exchange.assert_called_once_with(
            OwnerSocialIdentity.Provider.FACEBOOK,
            "provider-code",
        )
        mock_profile.assert_called_once_with(
            OwnerSocialIdentity.Provider.FACEBOOK,
            "temporary-access-token",
        )
        mock_bind.assert_called_once_with(
            self.owner_entity,
            OwnerSocialIdentity.Provider.FACEBOOK,
            "facebook-owner-123",
            "owner",
        )

    @override_settings(
        OWNER_FACEBOOK_OAUTH_CLIENT_ID="facebook-client",
        OWNER_FACEBOOK_OAUTH_CLIENT_SECRET="facebook-secret",
        OWNER_FACEBOOK_OAUTH_TOKEN_ENDPOINT="https://graph.facebook.com/oauth/access_token",
        OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT="https://www.facebook.com/dialog/oauth",
        OWNER_FACEBOOK_OAUTH_REDIRECT_URI="https://zootasks.example/accounts/owner/social/facebook/callback/",
        OWNER_FACEBOOK_OAUTH_SCOPES="scope_a",
        OWNER_FACEBOOK_OAUTH_PROFILE_ENDPOINT="https://graph.facebook.com/me",
        OWNER_FACEBOOK_OAUTH_PROFILE_FIELDS="id,name",
    )
    @patch("accounts.views.get_owner_social_profile")
    @patch("accounts.views.exchange_owner_social_authorization_code")
    def test_callback_exchange_failure_does_not_bind_identity(
        self,
        mock_exchange,
        mock_profile,
    ):
        self.client.force_login(self.owner)
        state = "exchange-failure-state"
        OwnerSocialOAuthState.objects.create(
            account_entity=self.owner_entity,
            provider=OwnerSocialIdentity.Provider.FACEBOOK,
            state_hash=__import__("hashlib").sha256(
                state.encode("utf-8")
            ).hexdigest(),
            expires_at=__import__("django.utils.timezone").utils.timezone.now()
            + __import__("datetime").timedelta(minutes=10),
        )
        mock_exchange.side_effect = ValueError("exchange failed")

        response = self.client.get(
            reverse(
                "owner_social_oauth_callback",
                kwargs={"provider": OwnerSocialIdentity.Provider.FACEBOOK},
            ),
            {"state": state, "code": "provider-code"},
        )

        self.assertEqual(response.status_code, 400)
        mock_exchange.assert_called_once_with(
            OwnerSocialIdentity.Provider.FACEBOOK,
            "provider-code",
        )
        mock_profile.assert_not_called()
        self.assertFalse(
            OwnerSocialIdentity.objects.filter(
                account_entity=self.owner_entity,
            ).exists()
        )

    @override_settings(
        OWNER_FACEBOOK_OAUTH_CLIENT_ID="facebook-client",
        OWNER_FACEBOOK_OAUTH_CLIENT_SECRET="facebook-secret",
        OWNER_FACEBOOK_OAUTH_TOKEN_ENDPOINT="https://graph.facebook.com/oauth/access_token",
        OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT="https://www.facebook.com/dialog/oauth",
        OWNER_FACEBOOK_OAUTH_REDIRECT_URI="https://zootasks.example/accounts/owner/social/facebook/callback/",
        OWNER_FACEBOOK_OAUTH_SCOPES="scope_a",
        OWNER_FACEBOOK_OAUTH_PROFILE_ENDPOINT="https://graph.facebook.com/me",
        OWNER_FACEBOOK_OAUTH_PROFILE_FIELDS="id,name",
    )
    @patch("accounts.views.bind_verified_owner_social_identity")
    @patch("accounts.views.get_owner_social_profile")
    @patch("accounts.views.exchange_owner_social_authorization_code")
    def test_callback_profile_failure_does_not_bind_identity(
        self,
        mock_exchange,
        mock_profile,
        mock_bind,
    ):
        from accounts.social_oauth_exchange import OwnerSocialOAuthTokenResponse

        self.client.force_login(self.owner)
        state = "profile-failure-state"
        OwnerSocialOAuthState.objects.create(
            account_entity=self.owner_entity,
            provider=OwnerSocialIdentity.Provider.FACEBOOK,
            state_hash=__import__("hashlib").sha256(
                state.encode("utf-8")
            ).hexdigest(),
            expires_at=__import__("django.utils.timezone").utils.timezone.now()
            + __import__("datetime").timedelta(minutes=10),
        )
        mock_exchange.return_value = OwnerSocialOAuthTokenResponse(
            access_token="temporary-access-token",
            token_type="Bearer",
            expires_in=3600,
        )
        mock_profile.side_effect = ValueError("profile failed")

        response = self.client.get(
            reverse(
                "owner_social_oauth_callback",
                kwargs={"provider": OwnerSocialIdentity.Provider.FACEBOOK},
            ),
            {"state": state, "code": "provider-code"},
        )

        self.assertEqual(response.status_code, 400)
        mock_bind.assert_not_called()
        self.assertFalse(
            OwnerSocialIdentity.objects.filter(
                account_entity=self.owner_entity,
            ).exists()
        )

    def test_callback_rejects_replayed_state(self):
        self.client.force_login(self.owner)
        state = "replayed-state"
        challenge = OwnerSocialOAuthState.objects.create(
            account_entity=self.owner_entity,
            provider=OwnerSocialIdentity.Provider.FACEBOOK,
            state_hash=__import__("hashlib").sha256(
                state.encode("utf-8")
            ).hexdigest(),
            expires_at=__import__("django.utils.timezone").utils.timezone.now()
            + __import__("datetime").timedelta(minutes=10),
        )
        challenge.used_at = __import__("django.utils.timezone").utils.timezone.now()
        challenge.save(update_fields=["used_at"])

        response = self.client.get(
            reverse(
                "owner_social_oauth_callback",
                kwargs={"provider": OwnerSocialIdentity.Provider.FACEBOOK},
            ),
            {"state": state, "code": "provider-code"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(
            OwnerSocialIdentity.objects.filter(
                account_entity=self.owner_entity,
            ).exists()
        )

    def test_callback_consumes_matching_state_but_does_not_store_provider_token(self):
        self.client.force_login(self.owner)
        state = "test-state"
        challenge = OwnerSocialOAuthState.objects.create(
            account_entity=self.owner_entity,
            provider=OwnerSocialIdentity.Provider.FACEBOOK,
            state_hash=__import__("hashlib").sha256(
                state.encode("utf-8")
            ).hexdigest(),
            expires_at=__import__("django.utils.timezone").utils.timezone.now()
            + __import__("datetime").timedelta(minutes=10),
        )

        response = self.client.get(
            reverse(
                "owner_social_oauth_callback",
                kwargs={"provider": OwnerSocialIdentity.Provider.FACEBOOK},
            ),
            {"state": state, "code": "provider-code"},
        )

        self.assertEqual(response.status_code, 400)
        challenge.refresh_from_db()
        self.assertIsNotNone(challenge.used_at)
        self.assertFalse(hasattr(OwnerSocialIdentity, "access_token"))
