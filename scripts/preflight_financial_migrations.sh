#!/usr/bin/env bash
set -euo pipefail
umask 077

if [[ -z "${DATABASE_URL:-}" ]]; then
    printf '%s\n' "FAIL: DATABASE_URL must be supplied through a secure environment." >&2
    exit 2
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
RESULTS="$(mktemp)"
trap 'rm -f "$RESULTS"' EXIT

# Do not enable shell tracing or print DATABASE_URL. Query output contains only
# invariant names and aggregate counts, never financial or identity records.
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -At -F '|' \
    -f "$SCRIPT_DIR/preflight_financial_migrations.sql" > "$RESULTS"

cat "$RESULTS"

if awk -F'|' '$2 !~ /^[0-9]+$/ || ($2 + 0) != 0 { bad = 1 } END { exit(bad ? 0 : 1) }' "$RESULTS"; then
    printf '%s\n' "FAIL: migration preflight found invariant violations; do not migrate until reviewed and reconciled." >&2
    exit 1
fi

printf '%s\n' "PASS: all checked financial migration invariants are clear."
