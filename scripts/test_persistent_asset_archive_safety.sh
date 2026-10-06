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

mkdir -p "$ROOT/absolute"
printf 'synthetic' > "$ROOT/absolute/file"
tar -czf "$ROOT/absolute.tar.gz" -C "$ROOT" absolute
chmod 600 "$ROOT/absolute.tar.gz"
python3 - "$ROOT/absolute.tar.gz" <<'PY'
import sys
from pathlib import Path
import tarfile

archive = Path(sys.argv[1])
tmp = archive.with_suffix(".rewrite.tar.gz")
with tarfile.open(archive, "r:gz") as src, tarfile.open(tmp, "w:gz") as dst:
    for member in src:
        if member.name == "absolute":
            member.name = "/absolute"
        dst.addfile(member, src.extractfile(member) if member.isfile() else None)
tmp.replace(archive)
PY
if bash scripts/verify_persistent_asset_archive.sh "$ROOT/absolute.tar.gz" >/dev/null 2>&1; then
  echo "FAIL: absolute archive path was accepted" >&2
  exit 1
fi

mkdir -p "$ROOT/link"
printf 'synthetic' > "$ROOT/link/target"
ln -s target "$ROOT/link/symlink"
tar -czf "$ROOT/symlink.tar.gz" -C "$ROOT" link
chmod 600 "$ROOT/symlink.tar.gz"
if bash scripts/verify_persistent_asset_archive.sh "$ROOT/symlink.tar.gz" >/dev/null 2>&1; then
  echo "FAIL: symlink archive entry was accepted" >&2
  exit 1
fi

echo "PASS: persistent-asset archive safety tests"
