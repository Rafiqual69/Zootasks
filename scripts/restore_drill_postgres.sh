#!/usr/bin/env bash
set -euo pipefail
umask 077

usage(){ echo 'Usage: $0 <dump-file> <admin-database-url> <restore-database-name>' >&2; exit 2; }
[[ $# -eq 3 ]] || usage
DUMP_FILE="$1"
ADMIN_URL="$2"
RESTORE_DB="$3"
[[ -f "$DUMP_FILE" ]] || { echo 'FAIL: dump file not found' >&2; exit 1; }
[[ "$RESTORE_DB" =~ ^restore_drill_[a-zA-Z0-9_]+$ ]] || { echo 'FAIL: target must start with restore_drill_' >&2; exit 1; }
HOST="$(python3 -c 'import sys; from urllib.parse import urlparse; print(urlparse(sys.argv[1]).hostname or "")' "$ADMIN_URL")"
case "$HOST" in localhost|127.0.0.1|::1) ;; *) echo 'FAIL: non-local database host refused' >&2; exit 1 ;; esac
command -v psql >/dev/null || { echo 'FAIL: psql required' >&2; exit 1; }
command -v pg_restore >/dev/null || { echo 'FAIL: pg_restore required' >&2; exit 1; }
if psql "$ADMIN_URL" -tAc "SELECT 1 FROM pg_database WHERE datname = '$RESTORE_DB'" | grep -q 1; then echo 'FAIL: existing restore target; refusing overwrite' >&2; exit 1; fi
psql "$ADMIN_URL" -v ON_ERROR_STOP=1 -c "CREATE DATABASE \"$RESTORE_DB\""
cleanup(){ psql "$ADMIN_URL" -v ON_ERROR_STOP=1 -c "DROP DATABASE IF EXISTS \"$RESTORE_DB\"" >/dev/null 2>&1 || true; }
trap cleanup EXIT
BASE_URL="${ADMIN_URL%/*}/$RESTORE_DB"
pg_restore --dbname="$BASE_URL" --no-owner --exit-on-error "$DUMP_FILE"
TABLE_COUNT="$(psql "$BASE_URL" -tAc "SELECT count(*) FROM pg_catalog.pg_class WHERE relkind IN ('r','p')" | tr -d '[:space:]')"
[[ "$TABLE_COUNT" =~ ^[1-9][0-9]*$ ]] || { echo 'FAIL: restored database has no tables' >&2; exit 1; }
echo "PASS: isolated PostgreSQL restore drill completed; table_count=$TABLE_COUNT"
