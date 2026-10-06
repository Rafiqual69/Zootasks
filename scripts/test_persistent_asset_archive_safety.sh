#!/usr/bin/env bash
set -euo pipefail
umask 077

ROOT=$(mktemp -d)
trap 'rm -rf "$ROOT"' EXIT

mkdir -p "$ROOT/media"
printf 'synthetic-media' > "$ROOT/media/example.txt"
tar -czf "$ROOT/good.tar.gz" -C "$ROOT" media
chmod 600 "$ROOT/good.tar.gz"
bash scripts/verify_persistent_asset_archive.sh "$ROOT/good.tar.gz"

mkdir -p "$ROOT/bad/.git"
printf 'synthetic' > "$ROOT/bad/.git/config"
tar -czf "$ROOT/bad.tar.gz" -C "$ROOT" bad
chmod 600 "$ROOT/bad.tar.gz"
if bash scripts/verify_persistent_asset_archive.sh "$ROOT/bad.tar.gz" >/dev/null 2>&1; then
  echo "FAIL: prohibited .git content was accepted" >&2
  exit 1
fi

mkdir -p "$ROOT/secret"
printf 'synthetic' > "$ROOT/secret/token"
tar -czf "$ROOT/secret.tar.gz" -C "$ROOT" secret
chmod 600 "$ROOT/secret.tar.gz"
if bash scripts/verify_persistent_asset_archive.sh "$ROOT/secret.tar.gz" >/dev/null 2>&1; then
  echo "FAIL: prohibited secret path was accepted" >&2
  exit 1
fi

echo "PASS: persistent-asset archive safety tests"
