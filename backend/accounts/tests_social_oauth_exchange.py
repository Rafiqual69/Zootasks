import json
from unittest.mock import patch

from django.test import TestCase, override_settings

from accounts.models import OwnerSocialIdentity
from accounts.social_oauth_exchange import exchange_owner_social_authorization_code


class OwnerSocialOAuthExchangeTests(TestCase):
    @override_settings(
        OWNER_FACEBOOK_OAUTH_CLIENT_ID="client-id",
        OWNER_FACEBOOK_OAUTH_CLIENT_SECRET="secret-value",
        OWNER_FACEBOOK_OAUTH_TOKEN_ENDPOINT="https://provider.example/token",
        OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT="https://provider.example/authorize",
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
        OWNER_FACEBOOK_OAUTH_TOKEN_ENDPOINT="https://provider.example/token",
        OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT="https://provider.example/authorize",
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
        OWNER_FACEBOOK_OAUTH_TOKEN_ENDPOINT="https://provider.example/token",
        OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT="https://provider.example/authorize",
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
