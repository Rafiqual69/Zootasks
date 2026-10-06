# ZooTasks production deployment architecture

## Target architecture

```
Internet
  |
  | HTTPS
  v
Railway public web service
  |
  | private service networking
  +----> Railway PostgreSQL
  |
  +----> Railway Redis (when Celery workers are enabled)
  |
  +----> Celery worker / scheduler services
```

The web service is the only component that should receive public application traffic.
PostgreSQL and Redis should remain private to the Railway project/environment.

## Application service

- Build from the repository-root `Dockerfile`.
- The Docker image uses `backend/` as the Django working directory.
- Gunicorn serves `config.wsgi:application`.
- Static files are collected during the Railway pre-deploy phase.
- Database migrations run during the Railway pre-deploy phase.
- Production configuration is supplied through Railway Variables, not committed files.
- `PRODUCTION_MODE=True` is required for the production environment.

## Database

Local development uses SQLite.

Production uses PostgreSQL through `DATABASE_URL`. The application refuses to silently fall back to SQLite when `PRODUCTION_MODE=True` and no `DATABASE_URL` is supplied.

Railway's PostgreSQL service exposes `DATABASE_URL` and related connection variables. The production deployment should use the private database connection.

## HTTPS and proxy trust

The public service must be HTTPS-only.

If TLS terminates at a trusted reverse proxy and the proxy reliably sets `X-Forwarded-Proto: https`, set:

```
TRUST_PROXY_SSL=True
```

Do not enable this merely because a proxy exists; the proxy must be configured to prevent clients from spoofing the trusted header.

## HSTS

Production defaults to one year of HSTS and includes subdomains.

HSTS preload remains opt-in. It should only be enabled after the apex domain and every relevant subdomain have been verified to work exclusively over HTTPS.

## Secrets

The following values belong only in the deployment provider's secret/variable store:

- `SECRET_KEY`
- `DATABASE_URL` when it contains credentials
- `EMAIL_HOST_PASSWORD`
- `TELEGRAM_BOT_TOKEN`
- `AIRTM_API_KEY`
- `AIRTM_API_SECRET`

Never commit a real `.env` file.

## Deployment gate

Before a production deployment is allowed:

1. Django system check passes.
2. Migration drift check passes.
3. Full regression tests pass.
4. Security/dependency audit passes.
5. Production-mode `manage.py check --deploy` returns zero warnings.
6. The deployed service has verified HTTPS and the expected hostnames.
7. Database and other private services are not publicly exposed.

This architecture follows Django's deployment checklist and the project's SSDF/security-gate workflow.
