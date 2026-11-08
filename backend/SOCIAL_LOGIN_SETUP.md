# ZooTasks social sign-in setup

The login page supports four optional OAuth providers. Each provider remains hidden until both of its credentials are configured in the deployment environment.

## Environment secrets

Set these values in the hosting provider's secret manager. Do not commit real credentials to Git or paste them into issue comments.

- `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET`
- `FACEBOOK_OAUTH_CLIENT_ID` and `FACEBOOK_OAUTH_CLIENT_SECRET`
- `LINKEDIN_OAUTH_CLIENT_ID` and `LINKEDIN_OAUTH_CLIENT_SECRET`
- `YAHOO_OAUTH_CLIENT_ID` and `YAHOO_OAUTH_CLIENT_SECRET`

## OAuth callback URLs

Register the exact HTTPS callback URL for the production domain with each provider. For local testing, use the matching localhost callback registered in the provider console.

- Google: `https://www.zootasks.com/accounts/google/login/callback/`
- Facebook: `https://www.zootasks.com/accounts/facebook/login/callback/`
- LinkedIn: `https://www.zootasks.com/accounts/oidc/linkedin/login/callback/`
- Yahoo: `https://www.zootasks.com/accounts/yahoo/login/callback/`

The production domain above is a planned ZooTasks domain. Do not activate a provider until DNS, HTTPS, and the matching OAuth application redirect URI are confirmed for the actual deployment hostname.

## Security rules

- Missing credentials disable that provider's button.
- OAuth access tokens are not stored in the database.
- Provider email matches do not automatically link to existing ZooTasks accounts.
- Users must authenticate to their existing ZooTasks account before connecting an additional provider.
- Social sign-in cannot authenticate staff, superusers, or the privileged Owner account.
- New social signups are provisioned as ordinary workers using the existing WorkerProfile and AccountEntity records.
- Owner access remains on the separate password + TOTP login route.

## WhatsApp

WhatsApp is not an OAuth identity provider. A WhatsApp sign-in option must use a verified phone-number OTP flow backed by the official WhatsApp Business Platform (or an approved provider such as Twilio Verify). It needs a business sender, server-side credentials, an approved authentication message template, OTP expiry, attempt limits, resend cooldowns, and abuse controls. This branch does not enable WhatsApp OTP or expose a non-functional WhatsApp button.

## Activation checklist

1. Create and verify the OAuth application with each provider.
2. Register the exact callback URL and enable only the minimum profile/email scopes.
3. Store credentials in the production secret manager.
4. Run migrations and the full test suite in a staging environment.
5. Test new signups, existing-account linking, denied email-only auto-linking, and privileged-account rejection.
6. Enable one provider at a time after review.
