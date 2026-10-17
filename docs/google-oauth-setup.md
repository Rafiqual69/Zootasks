# Secure Google Sign-In Setup

Google sign-in uses the official OpenID Connect/OAuth flow through `django-allauth`. ZooTasks never asks users for their Google password.

## 1. Create the Google OAuth client

1. In Google Cloud Console, create or select the ZooTasks project.
2. Configure the OAuth consent screen and publish/test it according to the intended rollout.
3. Create an OAuth client with application type **Web application**.
4. Add the exact production origin to **Authorized JavaScript origins** when required by Google.
5. Add this exact callback URI to **Authorized redirect URIs**:
   `https://www.zootasks.com/accounts/google/login/callback/`
6. For local development only, use a separate test client and callback:
   `http://127.0.0.1:8000/accounts/google/login/callback/`

Never use a production client secret in local test files or commit it to Git.

## 2. Set deployment secrets

In the deployment provider's secret/variable store, configure:

- `GOOGLE_OAUTH_CLIENT_ID`: the Web application client ID.
- `GOOGLE_OAUTH_CLIENT_SECRET`: the matching client secret.

Both values must be present before the Google button is shown. Keep both values out of Git, issue comments, logs, screenshots, and chat messages. Do not paste the client secret into a repository file.

## 3. Security properties

- Uses OAuth/OpenID Connect through django-allauth, including state validation and PKCE.
- The Google login initiation is POST-based and protected by Django CSRF middleware.
- Requests only `openid`, `profile`, and `email` scopes; offline refresh tokens are not requested.
- OAuth access/refresh tokens are not stored by ZooTasks.
- A matching email alone does not automatically link a Google identity to an existing local account. Users with existing accounts should first sign in through their existing method and explicitly connect a provider from an authenticated account flow, where available.
- New Google signups receive a normal active Worker account and WorkerProfile. Google sign-in does not grant Owner, staff, superuser, wallet adjustment, or withdrawal approval privileges.
- Existing username/password login remains available.
- Google sign-in stays disabled if either OAuth environment variable is missing.

## 4. Before enabling production sign-in

1. Run the full CI suite, including account, authorization, wallet, withdrawal, and PostgreSQL financial verification tests.
2. Apply the package migrations in a controlled deployment process before serving the new code.
3. Confirm the production domain, HTTPS, allowed hosts, CSRF trusted origins, and Google callback URI match exactly.
4. Test new-user signup, an existing email collision, cancellation/denial, invalid state, callback mismatch, and ordinary password login.
5. Verify a Google-created user is a worker and cannot access Owner/admin controls.
6. Enable the environment variables only after review; deploy only after required checks pass and a human authorizes the production rollout.

Adding this code does not itself configure Google Cloud or enable production login.
