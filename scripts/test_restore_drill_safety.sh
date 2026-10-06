#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
touch "$TMP/empty.dump"

if PGADMIN_URL='postgresql://redacted:secret@production.example.invalid:5432/db' bash "$ROOT/scripts/restore_drill_postgres.sh" "$TMP/empty.dump" restore_drill_ci 2>"$TMP/err"; then
  echo 'FAIL: remote database host was accepted' >&2
  exit 1
fi
grep -q 'non-local database host refused' "$TMP/err"

if PGADMIN_URL='postgresql://localhost:5432/postgres' bash "$ROOT/scripts/restore_drill_postgres.sh" "$TMP/empty.dump" unsafe_name 2>"$TMP/err2"; then
  echo 'FAIL: unsafe restore database name was accepted' >&2
  exit 1
fi
grep -q 'target must start with restore_drill_' "$TMP/err2"

echo 'PASS: restore-drill safety boundary tests passed'
