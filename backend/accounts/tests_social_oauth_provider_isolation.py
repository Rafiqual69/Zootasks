from django.test import SimpleTestCase, override_settings

from accounts.models import OwnerSocialIdentity
from accounts.social_oauth_provider import get_owner_social_oauth_provider_config


class OwnerSocialOAuthProviderIsolationTests(SimpleTestCase):
    @override_settings(
        OWNER_FACEBOOK_OAUTH_CLIENT_ID="facebook-client",
        OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT="https://www.instagram.com/oauth/authorize",
        OWNER_FACEBOOK_OAUTH_TOKEN_ENDPOINT="https://graph.facebook.com/oauth/access_token",
        OWNER_FACEBOOK_OAUTH_REDIRECT_URI="https://zootasks.example/callback/",
        OWNER_FACEBOOK_OAUTH_SCOPES="scope_a",
    )
    def test_facebook_rejects_instagram_authorization_host(self):
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
        OWNER_INSTAGRAM_OAUTH_TOKEN_ENDPOINT="https://graph.facebook.com/oauth/access_token",
        OWNER_INSTAGRAM_OAUTH_REDIRECT_URI="https://zootasks.example/callback/",
        OWNER_INSTAGRAM_OAUTH_SCOPES="instagram_business_basic",
    )
    def test_instagram_rejects_facebook_token_host(self):
        with self.assertRaisesMessage(
            ValueError,
            "uses an unapproved OAuth host.",
        ):
            get_owner_social_oauth_provider_config(
                OwnerSocialIdentity.Provider.INSTAGRAM,
            )

    @override_settings(
        OWNER_INSTAGRAM_OAUTH_CLIENT_ID="instagram-client",
        OWNER_INSTAGRAM_OAUTH_AUTHORIZATION_ENDPOINT="https://www.instagram.com/oauth/authorize",
        OWNER_INSTAGRAM_OAUTH_TOKEN_ENDPOINT="https://api.instagram.com/oauth/access_token",
        OWNER_INSTAGRAM_OAUTH_REDIRECT_URI="https://zootasks.example/callback/",
        OWNER_INSTAGRAM_OAUTH_SCOPES="instagram_business_basic",
    )
    def test_instagram_provider_hosts_remain_valid(self):
        config = get_owner_social_oauth_provider_config(
            OwnerSocialIdentity.Provider.INSTAGRAM,
        )
        self.assertEqual(
            config.token_endpoint,
            "https://api.instagram.com/oauth/access_token",
        )
