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


## WhatsApp OTP login (separate from OAuth)

WhatsApp is not an OAuth identity provider. ZooTasks implements a separate phone-verification flow using Meta's WhatsApp Business Cloud API. The login route is `/accounts/whatsapp/login/`.

### Meta setup

1. Create a Meta business portfolio and WhatsApp Business Account, add/verify a business sender number, and create a Meta developer app with WhatsApp product.
2. Generate a production system-user access token with only the required `whatsapp_business_messaging` permission for sending messages. Keep it in the hosting provider's secret manager.
3. In WhatsApp Manager, create an **Authentication** template with a **Copy Code OTP** button. Use template name `zootasks_login_otp`, language `en_US`, and a five-minute expiry. Submit it for Meta approval and wait until its status is APPROVED.
4. Configure these server environment variables:
   - `META_WHATSAPP_ACCESS_TOKEN`
   - `META_WHATSAPP_PHONE_NUMBER_ID`
   - `META_WHATSAPP_GRAPH_API_VERSION` (default `v26.0`; use a currently supported version for the app)
   - `META_WHATSAPP_OTP_TEMPLATE_NAME` (default `zootasks_login_otp`)
   - `META_WHATSAPP_OTP_LANGUAGE_CODE` (default `en_US`)
5. Apply the new accounts migration in staging, then test with an opted-in test recipient before enabling production.

Create the template as an Authentication category with Meta's preset verification-code body, a Copy Code OTP button, and a five-minute code-expiration footer. The API sends an approved authentication template to `/{PHONE_NUMBER_ID}/messages`. Meta's Cloud API requires a WhatsApp Business Account, business phone number and access token; Meta's official collection documents the required permissions and message endpoint. See [Meta's WhatsApp Cloud API collection](https://www.postman.com/meta/whatsapp-business-platform/documentation/wlk6lh4/whatsapp-cloud-api) and [authentication template example](https://www.postman.com/meta/whatsapp-business-platform/request/6vkv46u/create-authentication-template-w-otp-copy-code-button).

### Application controls

- Phone numbers are normalized to E.164; Bangladesh local `01XXXXXXXXX` input is normalized to `+8801XXXXXXXXX`.
- Codes are cryptographically random, valid for five minutes, stored only as keyed HMAC digests, and never written to logs.
- Five verification attempts maximum; 60-second resend cooldown; per-phone and per-IP hourly send limits.
- OTP initiation and verification use POST with Django CSRF protection.
- A new account is created as a normal Worker only after phone verification. Existing verified numbers sign in to their linked Worker account.
- An authenticated Worker can link a phone only after OTP verification. A phone already linked to another account cannot be transferred this way.
- Staff, superusers, Owner accounts and inactive accounts cannot use WhatsApp OTP login.
- Provider credentials are never sent to templates. Missing configuration disables the feature.
- The database stores the phone number for the verified identity and the active challenge; protect database backups and access accordingly.

Meta approval, production credentials, sender registration, HTTPS, staging tests and the production migration are external release gates. This branch does not activate the integration in production.

## Activation checklist

1. Create and verify the OAuth application with each provider.
2. Register the exact callback URL and enable only the minimum profile/email scopes.
3. Store credentials in the production secret manager.
4. Run migrations and the full test suite in a staging environment.
5. Test new signups, existing-account linking, denied email-only auto-linking, and privileged-account rejection.
6. Enable one provider at a time after review.
