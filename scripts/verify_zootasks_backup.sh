#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 BACKUP_ARCHIVE" >&2
  exit 2
}

[ "$#" -eq 1 ] || usage
ARCHIVE="$1"

[ -f "$ARCHIVE" ] || { echo "Backup is not a regular file" >&2; exit 1; }
[ "$(stat -c '%a' "$ARCHIVE")" = "600" ] || {
  echo "Backup permissions must be 600" >&2
  exit 1
}

# Verify gzip/container integrity before inspecting names.
gzip -t -- "$ARCHIVE"

LISTING="$(mktemp)"
cleanup() { rm -f -- "$LISTING"; }
trap cleanup EXIT INT TERM

tar -tzf "$ARCHIVE" > "$LISTING"

# Reject traversal and sensitive/runtime material. The archive must be
# self-contained recovery source, never a secret or production-state dump.
if grep -E -q '(^|/)\.\.(\/|$)' "$LISTING"; then
  echo "Unsafe path traversal entry detected" >&2
  exit 1
fi

if grep -E -q '(^|/)(\.env|\.env\.[^/]*|\.git(/|$)|db\.sqlite3$|backups?(/|$))' "$LISTING"; then
  echo "Forbidden secret/recovery/database entry detected" >&2
  exit 1
fi

if grep -E -q '(^|/)(.*\.sqlite3|.*\.sqlite3-[^/]*|.*\.db|.*\.log|.*\.bak|.*\.backup|.*-backup[^/]*)(/|$)' "$LISTING"; then
  echo "Forbidden local database/log/backup artifact detected" >&2
  exit 1
fi

echo "Backup verification: PASS"
echo "Archive: $ARCHIVE"
echo "Entries: $(wc -l < "$LISTING" | tr -d ' ')"
