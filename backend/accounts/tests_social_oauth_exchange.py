import json
from unittest.mock import patch

from urllib.request import Request

from django.test import TestCase, override_settings

from accounts.models import OwnerSocialIdentity
from accounts.social_oauth_exchange import exchange_owner_social_authorization_code


class OwnerSocialOAuthExchangeTests(TestCase):
    def test_oauth_redirects_are_rejected(self):
        from accounts.social_oauth_exchange import _NoRedirectHandler

        handler = _NoRedirectHandler()
        request = Request("https://graph.facebook.com/oauth/access_token")
        with self.assertRaisesMessage(
            ValueError,
            "Owner social OAuth redirects are not allowed.",
        ):
            handler.redirect_request(
                request,
                None,
                302,
                "Found",
                {},
                "https://evil.example/steal",
            )

    @override_settings(
        OWNER_FACEBOOK_OAUTH_CLIENT_ID="client-id",
        OWNER_FACEBOOK_OAUTH_CLIENT_SECRET="secret",
        OWNER_FACEBOOK_OAUTH_TOKEN_ENDPOINT="https://graph.facebook.com/oauth/access_token",
        OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT="https://www.facebook.com/dialog/oauth",
        OWNER_FACEBOOK_OAUTH_REDIRECT_URI="https://zootasks.example/callback",
        OWNER_FACEBOOK_OAUTH_SCOPES="scope_a",
    )
    @patch("accounts.social_oauth_exchange.urlopen")
    def test_oversized_token_response_is_rejected(self, mock_urlopen):
        response = mock_urlopen.return_value.__enter__.return_value
        response.read.return_value = b"x" * (64 * 1024 + 1)

        with self.assertRaisesMessage(
            ValueError,
            "Owner social OAuth token exchange failed.",
        ):
            exchange_owner_social_authorization_code(
                OwnerSocialIdentity.Provider.FACEBOOK,
                "code",
            )

    @override_settings(
        OWNER_FACEBOOK_OAUTH_CLIENT_ID="client-id",
        OWNER_FACEBOOK_OAUTH_CLIENT_SECRET="secret",
        OWNER_FACEBOOK_OAUTH_TOKEN_ENDPOINT="https://graph.facebook.com/oauth/access_token",
        OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT="https://www.facebook.com/dialog/oauth",
        OWNER_FACEBOOK_OAUTH_REDIRECT_URI="https://zootasks.example/callback",
        OWNER_FACEBOOK_OAUTH_SCOPES="scope_a",
        OWNER_FACEBOOK_OAUTH_PROFILE_ENDPOINT="https://graph.facebook.com/me",
        OWNER_FACEBOOK_OAUTH_PROFILE_FIELDS="id,name",
    )
    @patch("accounts.social_oauth_exchange.urlopen")
    def test_oversized_profile_response_is_rejected(self, mock_urlopen):
        response = mock_urlopen.return_value.__enter__.return_value
        response.read.return_value = b"x" * (64 * 1024 + 1)

        from accounts.social_oauth_exchange import get_owner_social_profile

        with self.assertRaisesMessage(
            ValueError,
            "Owner social OAuth profile request failed.",
        ):
            get_owner_social_profile(
                OwnerSocialIdentity.Provider.FACEBOOK,
                "temporary-access-token",
            )

    @override_settings(
        OWNER_FACEBOOK_OAUTH_CLIENT_ID="client-id",
        OWNER_FACEBOOK_OAUTH_CLIENT_SECRET="secret",
        OWNER_FACEBOOK_OAUTH_TOKEN_ENDPOINT="https://graph.facebook.com/oauth/access_token",
        OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT="https://www.facebook.com/dialog/oauth",
        OWNER_FACEBOOK_OAUTH_REDIRECT_URI="https://zootasks.example/callback",
        OWNER_FACEBOOK_OAUTH_SCOPES="scope_a",
    )
    @patch("accounts.social_oauth_exchange.urlopen")
    def test_non_object_token_response_is_rejected(self, mock_urlopen):
        response = mock_urlopen.return_value.__enter__.return_value
        response.read.return_value = b'["unexpected"]'

        with self.assertRaisesMessage(
            ValueError,
            "Owner social OAuth token response is invalid.",
        ):
            exchange_owner_social_authorization_code(
                OwnerSocialIdentity.Provider.FACEBOOK,
                "code",
            )


    @override_settings(
        OWNER_FACEBOOK_OAUTH_CLIENT_ID="client-id",
        OWNER_FACEBOOK_OAUTH_CLIENT_SECRET="secret",
        OWNER_FACEBOOK_OAUTH_TOKEN_ENDPOINT="https://graph.facebook.com/oauth/access_token",
        OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT="https://www.facebook.com/dialog/oauth",
        OWNER_FACEBOOK_OAUTH_REDIRECT_URI="https://zootasks.example/callback",
        OWNER_FACEBOOK_OAUTH_SCOPES="scope_a",
    )
    @patch("accounts.social_oauth_exchange.urlopen")
    def test_negative_token_expiry_is_rejected(self, mock_urlopen):
        response = mock_urlopen.return_value.__enter__.return_value
        response.read.return_value = json.dumps({
            "access_token": "provider-access-token",
            "token_type": "Bearer",
            "expires_in": -1,
        }).encode("utf-8")

        with self.assertRaisesMessage(
            ValueError,
            "Owner social OAuth token expiry is invalid.",
        ):
            exchange_owner_social_authorization_code(
                OwnerSocialIdentity.Provider.FACEBOOK,
                "code",
            )


    @override_settings(
        OWNER_FACEBOOK_OAUTH_CLIENT_ID="client-id",
        OWNER_FACEBOOK_OAUTH_CLIENT_SECRET="secret",
        OWNER_FACEBOOK_OAUTH_TOKEN_ENDPOINT="https://graph.facebook.com/oauth/access_token",
        OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT="https://www.facebook.com/dialog/oauth",
        OWNER_FACEBOOK_OAUTH_REDIRECT_URI="https://zootasks.example/callback",
        OWNER_FACEBOOK_OAUTH_SCOPES="scope_a",
    )
    @patch("accounts.social_oauth_exchange.urlopen")
    def test_non_success_token_http_status_is_rejected(self, mock_urlopen):
        response = mock_urlopen.return_value.__enter__.return_value
        response.status = 500
        response.read.return_value = b'{"access_token":"should-not-be-used"}'

        with self.assertRaisesMessage(
            ValueError,
            "Owner social OAuth token exchange failed.",
        ):
            exchange_owner_social_authorization_code(
                OwnerSocialIdentity.Provider.FACEBOOK,
                "code",
            )


    @override_settings(
        OWNER_FACEBOOK_OAUTH_CLIENT_ID="client-id",
        OWNER_FACEBOOK_OAUTH_CLIENT_SECRET="secret",
        OWNER_FACEBOOK_OAUTH_TOKEN_ENDPOINT="https://graph.facebook.com/oauth/access_token",
        OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT="https://www.facebook.com/dialog/oauth",
        OWNER_FACEBOOK_OAUTH_REDIRECT_URI="https://zootasks.example/callback",
        OWNER_FACEBOOK_OAUTH_SCOPES="scope_a",
        OWNER_FACEBOOK_OAUTH_PROFILE_ENDPOINT="https://graph.facebook.com/me",
        OWNER_FACEBOOK_OAUTH_PROFILE_FIELDS="id,name",
    )
    @patch("accounts.social_oauth_exchange.urlopen")
    def test_non_object_profile_response_is_rejected(self, mock_urlopen):
        response = mock_urlopen.return_value.__enter__.return_value
        response.read.return_value = b'["unexpected"]'

        from accounts.social_oauth_exchange import get_owner_social_profile

        with self.assertRaisesMessage(
            ValueError,
            "Owner social OAuth profile response is invalid.",
        ):
            get_owner_social_profile(
                OwnerSocialIdentity.Provider.FACEBOOK,
                "temporary-access-token",
            )


    @override_settings(
        OWNER_FACEBOOK_OAUTH_CLIENT_ID="client-id",
        OWNER_FACEBOOK_OAUTH_CLIENT_SECRET="secret",
        OWNER_FACEBOOK_OAUTH_TOKEN_ENDPOINT="https://graph.facebook.com/oauth/access_token",
        OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT="https://www.facebook.com/dialog/oauth",
        OWNER_FACEBOOK_OAUTH_REDIRECT_URI="https://zootasks.example/callback",
        OWNER_FACEBOOK_OAUTH_SCOPES="scope_a",
        OWNER_FACEBOOK_OAUTH_PROFILE_ENDPOINT="https://graph.facebook.com/me",
        OWNER_FACEBOOK_OAUTH_PROFILE_FIELDS="id,name",
    )
    @patch("accounts.social_oauth_exchange.urlopen")
    def test_non_success_profile_http_status_is_rejected(self, mock_urlopen):
        response = mock_urlopen.return_value.__enter__.return_value
        response.status = 503
        response.read.return_value = b'{"id":"should-not-be-used"}'

        from accounts.social_oauth_exchange import get_owner_social_profile

        with self.assertRaisesMessage(
            ValueError,
            "Owner social OAuth profile request failed.",
        ):
            get_owner_social_profile(
                OwnerSocialIdentity.Provider.FACEBOOK,
                "temporary-access-token",
            )


    @override_settings(
        OWNER_FACEBOOK_OAUTH_CLIENT_ID="client-id",
        OWNER_FACEBOOK_OAUTH_CLIENT_SECRET="secret-value",
        OWNER_FACEBOOK_OAUTH_TOKEN_ENDPOINT="https://graph.facebook.com/oauth/access_token",
        OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT="https://www.facebook.com/dialog/oauth",
        OWNER_FACEBOOK_OAUTH_REDIRECT_URI="https://zootasks.example/callback",
        OWNER_FACEBOOK_OAUTH_SCOPES="scope_a",
    )
    @patch("accounts.social_oauth_exchange.urlopen")
    def test_exchange_returns_token_without_persisting_it(self, mock_urlopen):
        response = mock_urlopen.return_value.__enter__.return_value
        response.read.return_value = json.dumps({
            "access_token": "provider-access-token",
            "token_type": "Bearer",
            "expires_in": 3600,
        }).encode("utf-8")

        result = exchange_owner_social_authorization_code(
            OwnerSocialIdentity.Provider.FACEBOOK,
            "code-with-special+chars",
        )

        self.assertEqual(result.access_token, "provider-access-token")
        self.assertEqual(result.expires_in, 3600)
        request = mock_urlopen.call_args.args[0]
        body = request.data.decode("utf-8")
        self.assertIn("client_secret=secret-value", body)
        self.assertIn("code=code-with-special%2Bchars", body)

    @override_settings(
        OWNER_FACEBOOK_OAUTH_CLIENT_ID="client-id",
        OWNER_FACEBOOK_OAUTH_CLIENT_SECRET="",
        OWNER_FACEBOOK_OAUTH_TOKEN_ENDPOINT="https://graph.facebook.com/oauth/access_token",
        OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT="https://www.facebook.com/dialog/oauth",
        OWNER_FACEBOOK_OAUTH_REDIRECT_URI="https://zootasks.example/callback",
        OWNER_FACEBOOK_OAUTH_SCOPES="scope_a",
    )
    def test_missing_client_secret_is_rejected(self):
        with self.assertRaisesMessage(
            ValueError,
            "Owner social OAuth client secret is not configured.",
        ):
            exchange_owner_social_authorization_code(
                OwnerSocialIdentity.Provider.FACEBOOK,
                "code",
            )

    @override_settings(
        OWNER_FACEBOOK_OAUTH_CLIENT_ID="client-id",
        OWNER_FACEBOOK_OAUTH_CLIENT_SECRET="secret",
        OWNER_FACEBOOK_OAUTH_TOKEN_ENDPOINT="https://graph.facebook.com/oauth/access_token",
        OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT="https://www.facebook.com/dialog/oauth",
        OWNER_FACEBOOK_OAUTH_REDIRECT_URI="https://zootasks.example/callback",
        OWNER_FACEBOOK_OAUTH_SCOPES="scope_a",
        OWNER_FACEBOOK_OAUTH_PROFILE_ENDPOINT="https://graph.facebook.com/me",
        OWNER_FACEBOOK_OAUTH_PROFILE_FIELDS="id,name",
    )
    @patch("accounts.social_oauth_exchange.urlopen")
    def test_profile_without_provider_id_is_rejected(self, mock_urlopen):
        response = mock_urlopen.return_value.__enter__.return_value
        response.read.return_value = b'{"name":"Owner"}'

        from accounts.social_oauth_exchange import get_owner_social_profile

        with self.assertRaisesMessage(
            ValueError,
            "Owner social OAuth profile response is invalid.",
        ):
            get_owner_social_profile(
                OwnerSocialIdentity.Provider.FACEBOOK,
                "temporary-access-token",
            )



    @override_settings(
        OWNER_FACEBOOK_OAUTH_CLIENT_ID="client-id",
        OWNER_FACEBOOK_OAUTH_CLIENT_SECRET="secret",
        OWNER_FACEBOOK_OAUTH_TOKEN_ENDPOINT="https://graph.facebook.com/oauth/access_token",
        OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT="https://www.facebook.com/dialog/oauth",
        OWNER_FACEBOOK_OAUTH_REDIRECT_URI="https://zootasks.example/callback",
        OWNER_FACEBOOK_OAUTH_SCOPES="scope_a",
        OWNER_FACEBOOK_OAUTH_PROFILE_ENDPOINT="https://evil.example/profile",
        OWNER_FACEBOOK_OAUTH_PROFILE_FIELDS="id,name",
    )
    def test_unapproved_profile_endpoint_is_rejected(self):
        from accounts.social_oauth_exchange import get_owner_social_profile

        with self.assertRaisesMessage(
            ValueError,
            "Owner social OAuth profile endpoint uses an unapproved host.",
        ):
            get_owner_social_profile(
                OwnerSocialIdentity.Provider.FACEBOOK,
                "temporary-access-token",
            )


    @override_settings(
        OWNER_FACEBOOK_OAUTH_CLIENT_ID="client-id",
        OWNER_FACEBOOK_OAUTH_CLIENT_SECRET="secret",
        OWNER_FACEBOOK_OAUTH_TOKEN_ENDPOINT="https://graph.facebook.com/oauth/access_token",
        OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT="https://www.facebook.com/dialog/oauth",
        OWNER_FACEBOOK_OAUTH_REDIRECT_URI="https://zootasks.example/callback",
        OWNER_FACEBOOK_OAUTH_SCOPES="scope_a",
    )
    @patch("accounts.social_oauth_exchange.urlopen")
    def test_invalid_token_response_is_rejected(self, mock_urlopen):
        response = mock_urlopen.return_value.__enter__.return_value
        response.read.return_value = b'{"token_type":"Bearer"}'

        with self.assertRaisesMessage(
            ValueError,
            "Owner social OAuth token response is invalid.",
        ):
            exchange_owner_social_authorization_code(
                OwnerSocialIdentity.Provider.FACEBOOK,
                "code",
            )


    @override_settings(
        OWNER_FACEBOOK_OAUTH_CLIENT_ID="client-id",
        OWNER_FACEBOOK_OAUTH_CLIENT_SECRET="secret",
        OWNER_FACEBOOK_OAUTH_TOKEN_ENDPOINT="https://graph.facebook.com/oauth/access_token",
        OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT="https://www.facebook.com/dialog/oauth",
        OWNER_FACEBOOK_OAUTH_REDIRECT_URI="https://zootasks.example/callback",
        OWNER_FACEBOOK_OAUTH_SCOPES="scope_a",
        OWNER_FACEBOOK_OAUTH_PROFILE_ENDPOINT="https://graph.facebook.com/me",
        OWNER_FACEBOOK_OAUTH_PROFILE_FIELDS="id,name",
    )
    @patch("accounts.social_oauth_exchange.urlopen")
    def test_profile_returns_verified_provider_id_without_persisting_token(self, mock_urlopen):
        response = mock_urlopen.return_value.__enter__.return_value
        response.read.return_value = b'{"id":"123456","name":"Owner"}'

        from accounts.social_oauth_exchange import get_owner_social_profile

        profile = get_owner_social_profile(
            OwnerSocialIdentity.Provider.FACEBOOK,
            "temporary-access-token",
        )

        self.assertEqual(profile.provider_user_id, "123456")
        self.assertEqual(profile.username, "")
        request = mock_urlopen.call_args.args[0]
        self.assertNotIn("access_token=", request.full_url)
        self.assertEqual(
            request.get_header("Authorization"),
            "Bearer temporary-access-token",
        )
