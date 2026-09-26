from django.test import SimpleTestCase, override_settings

from accounts.models import OwnerSocialIdentity
from accounts.social_oauth_provider import (
    build_owner_social_authorization_url,
    get_owner_social_oauth_provider_config,
)


class OwnerSocialOAuthProviderConfigTests(SimpleTestCase):
    @override_settings(
        OWNER_FACEBOOK_OAUTH_CLIENT_ID="facebook-client",
        OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT="https://provider.example/authorize",
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
        OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT="https://provider.example/authorize",
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
        OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT="https://provider.example/authorize",
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
        OWNER_INSTAGRAM_OAUTH_AUTHORIZATION_ENDPOINT="https://provider.example/authorize",
        OWNER_INSTAGRAM_OAUTH_REDIRECT_URI="https://zootasks.example/accounts/owner/social/instagram/callback/",
        OWNER_INSTAGRAM_OAUTH_SCOPES="scope_a",
    )
    def test_instagram_configuration_uses_separate_settings(self):
        config = get_owner_social_oauth_provider_config(
            OwnerSocialIdentity.Provider.INSTAGRAM,
        )
        self.assertEqual(config.provider, OwnerSocialIdentity.Provider.INSTAGRAM)
        self.assertEqual(config.client_id, "instagram-client")
