#!/usr/bin/env bash
set -euo pipefail

actual_sha="${RAILWAY_GIT_COMMIT_SHA:-}"
approved_sha="${ZOOTASKS_APPROVED_RELEASE_SHA:-}"

if [[ -z "$actual_sha" || "$approved_sha" != "$actual_sha" ]]; then
    printf '%s\n' "Release blocked: approve this exact reviewed commit by setting ZOOTASKS_APPROVED_RELEASE_SHA after backup, migration, and rollback checks." >&2
    exit 1
fi

if [[ "${PRODUCTION_MODE:-false}" != "true" ]]; then
    printf '%s\n' "Release blocked: PRODUCTION_MODE must be true." >&2
    exit 1
fi

if [[ -z "${SECRET_KEY:-}" || -z "${DATABASE_URL:-}" || -z "${ALLOWED_HOSTS:-}" ]]; then
    printf '%s\n' "Release blocked: required production configuration is missing." >&2
    exit 1
fi

cd /app/backend

# Never mutate the production schema automatically here. A separately reviewed
# release operator must apply migrations after a verified backup. This check
# refuses to deploy if any migration remains unapplied.
python manage.py migrate --check
python manage.py check --deploy
