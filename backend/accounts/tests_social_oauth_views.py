from django.contrib.auth.models import User
from django.test import TestCase, override_settings
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
        OWNER_FACEBOOK_OAUTH_AUTHORIZATION_ENDPOINT="https://provider.example/authorize",
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

        self.assertEqual(response.status_code, 501)
        challenge.refresh_from_db()
        self.assertIsNotNone(challenge.used_at)
        self.assertFalse(hasattr(OwnerSocialIdentity, "access_token"))
