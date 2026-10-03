from django.test import SimpleTestCase, override_settings

from accounts.models import OwnerSocialIdentity
from accounts.social_oauth_provider import (
    build_owner_social_authorization_url,
    get_owner_social_oauth_provider_config,
)


class OwnerSocialOAuthProviderConfigTests(SimpleTestCase):
    @override_settings(
        OWNER_FACEBOOK_OAUTH_CLIENT_ID="facebook-client",
        OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT="https://www.facebook.com/dialog/oauth",
        OWNER_FACEBOOK_OAUTH_TOKEN_ENDPOINT="https://graph.facebook.com/oauth/access_token",
        OWNER_FACEBOOK_OAUTH_REDIRECT_URI="https://zootasks.example/accounts/owner/social/facebook/callback/",
        OWNER_FACEBOOK_OAUTH_SCOPES="scope_a, scope_b",
    )
    def test_provider_config_is_loaded_without_exposing_secrets(self):
        config = get_owner_social_oauth_provider_config(
            OwnerSocialIdentity.Provider.FACEBOOK,
        )
        self.assertEqual(config.client_id, "facebook-client")
        self.assertEqual(config.scopes, ("scope_a", "scope_b"))

    @override_settings(
        OWNER_FACEBOOK_OAUTH_CLIENT_ID="facebook-client",
        OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT="https://www.facebook.com/dialog/oauth",
        OWNER_FACEBOOK_OAUTH_TOKEN_ENDPOINT="https://graph.facebook.com/oauth/access_token",
        OWNER_FACEBOOK_OAUTH_REDIRECT_URI="https://zootasks.example/accounts/owner/social/facebook/callback/",
        OWNER_FACEBOOK_OAUTH_SCOPES="scope_a,scope_b",
    )
    def test_authorization_url_contains_state_and_expected_parameters(self):
        url = build_owner_social_authorization_url(
            OwnerSocialIdentity.Provider.FACEBOOK,
            "random-state",
        )
        self.assertIn("client_id=facebook-client", url)
        self.assertIn("response_type=code", url)
        self.assertIn("scope=scope_a+scope_b", url)
        self.assertIn("state=random-state", url)

    @override_settings(
        OWNER_FACEBOOK_OAUTH_CLIENT_ID="",
        OWNER_FACEBOOK_OAUTH_TOKEN_ENDPOINT="https://graph.facebook.com/oauth/access_token",
        OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT="https://www.facebook.com/dialog/oauth",
        OWNER_FACEBOOK_OAUTH_REDIRECT_URI="https://zootasks.example/callback/",
        OWNER_FACEBOOK_OAUTH_SCOPES="scope_a",
    )
    def test_missing_client_id_is_rejected(self):
        with self.assertRaises(ValueError):
            get_owner_social_oauth_provider_config(
                OwnerSocialIdentity.Provider.FACEBOOK,
            )

    @override_settings(
        OWNER_INSTAGRAM_OAUTH_CLIENT_ID="instagram-client",
        OWNER_INSTAGRAM_OAUTH_AUTHORIZATION_ENDPOINT="https://www.instagram.com/oauth/authorize",
        OWNER_INSTAGRAM_OAUTH_TOKEN_ENDPOINT="https://api.instagram.com/oauth/access_token",
        OWNER_INSTAGRAM_OAUTH_REDIRECT_URI="https://zootasks.example/accounts/owner/social/instagram/callback/",
        OWNER_INSTAGRAM_OAUTH_SCOPES="scope_a",
    )
    def test_instagram_configuration_uses_separate_settings(self):
        config = get_owner_social_oauth_provider_config(
            OwnerSocialIdentity.Provider.INSTAGRAM,
        )
        self.assertEqual(config.provider, OwnerSocialIdentity.Provider.INSTAGRAM)
        self.assertEqual(config.client_id, "instagram-client")


    @override_settings(
        OWNER_FACEBOOK_OAUTH_CLIENT_ID="facebook-client",
        OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT="https://evil.example/authorize",
        OWNER_FACEBOOK_OAUTH_TOKEN_ENDPOINT="https://graph.facebook.com/oauth/access_token",
        OWNER_FACEBOOK_OAUTH_REDIRECT_URI="https://zootasks.example/callback/",
        OWNER_FACEBOOK_OAUTH_SCOPES="scope_a",
    )
    def test_unapproved_oauth_host_is_rejected(self):
        with self.assertRaisesMessage(
            ValueError,
            "uses an unapproved OAuth host.",
        ):
            get_owner_social_oauth_provider_config(
                OwnerSocialIdentity.Provider.FACEBOOK,
            )

    @override_settings(
        OWNER_INSTAGRAM_OAUTH_CLIENT_ID="instagram-client",
        OWNER_INSTAGRAM_OAUTH_AUTHORIZATION_ENDPOINT="https://www.instagram.com/oauth/authorize",
        OWNER_INSTAGRAM_OAUTH_TOKEN_ENDPOINT="https://api.instagram.com/oauth/access_token",
        OWNER_INSTAGRAM_OAUTH_REDIRECT_URI="https://zootasks.example/callback/",
        OWNER_INSTAGRAM_OAUTH_SCOPES="instagram_business_basic",
    )
    def test_instagram_meta_hosts_are_allowed(self):
        config = get_owner_social_oauth_provider_config(
            OwnerSocialIdentity.Provider.INSTAGRAM,
        )
        self.assertEqual(config.token_endpoint, "https://api.instagram.com/oauth/access_token")

    @override_settings(
        PRODUCTION_MODE=True,
        OWNER_FACEBOOK_OAUTH_CLIENT_ID="facebook-client",
        OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT="https://www.facebook.com/dialog/oauth",
        OWNER_FACEBOOK_OAUTH_TOKEN_ENDPOINT="https://graph.facebook.com/oauth/access_token",
        OWNER_FACEBOOK_OAUTH_REDIRECT_URI="http://zootasks.example/accounts/callback/",
        OWNER_FACEBOOK_OAUTH_SCOPES="scope_a",
    )
    def test_production_rejects_http_redirect_uri(self):
        with self.assertRaisesMessage(
            ValueError,
            "must use HTTPS outside localhost development.",
        ):
            get_owner_social_oauth_provider_config(
                OwnerSocialIdentity.Provider.FACEBOOK,
            )

    @override_settings(
        PRODUCTION_MODE=False,
        OWNER_FACEBOOK_OAUTH_CLIENT_ID="facebook-client",
        OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT="https://www.facebook.com/dialog/oauth",
        OWNER_FACEBOOK_OAUTH_TOKEN_ENDPOINT="https://graph.facebook.com/oauth/access_token",
        OWNER_FACEBOOK_OAUTH_REDIRECT_URI="http://evil.example/accounts/callback/",
        OWNER_FACEBOOK_OAUTH_SCOPES="scope_a",
    )
    def test_development_rejects_non_loopback_http_redirect_uri(self):
        with self.assertRaisesMessage(
            ValueError,
            "must use HTTPS outside localhost development.",
        ):
            get_owner_social_oauth_provider_config(
                OwnerSocialIdentity.Provider.FACEBOOK,
            )

    @override_settings(
        PRODUCTION_MODE=False,
        OWNER_FACEBOOK_OAUTH_CLIENT_ID="facebook-client",
        OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT="https://www.facebook.com/dialog/oauth",
        OWNER_FACEBOOK_OAUTH_TOKEN_ENDPOINT="https://graph.facebook.com/oauth/access_token",
        OWNER_FACEBOOK_OAUTH_REDIRECT_URI="http://127.0.0.1:8000/accounts/callback/",
        OWNER_FACEBOOK_OAUTH_SCOPES="scope_a",
    )
    def test_development_allows_loopback_http_redirect_uri(self):
        config = get_owner_social_oauth_provider_config(
            OwnerSocialIdentity.Provider.FACEBOOK,
        )
        self.assertEqual(
            config.redirect_uri,
            "http://127.0.0.1:8000/accounts/callback/",
        )

    @override_settings(
        OWNER_FACEBOOK_OAUTH_CLIENT_ID="facebook-client",
        OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT="https://www.facebook.com/dialog/oauth",
        OWNER_FACEBOOK_OAUTH_TOKEN_ENDPOINT="https://graph.facebook.com/oauth/access_token",
        OWNER_FACEBOOK_OAUTH_REDIRECT_URI="https://zootasks.example/accounts/callback/#fragment",
        OWNER_FACEBOOK_OAUTH_SCOPES="scope_a",
    )
    def test_redirect_uri_fragment_is_rejected(self):
        with self.assertRaisesMessage(
            ValueError,
            "absolute HTTPS redirect URI",
        ):
            get_owner_social_oauth_provider_config(
                OwnerSocialIdentity.Provider.FACEBOOK,
            )
