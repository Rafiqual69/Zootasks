#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "usage: $0 <archive.tar.gz>" >&2
  exit 2
}

[[ $# -eq 1 ]] || usage
ARCHIVE=$1
[[ -f "$ARCHIVE" ]] || { echo "FAIL: archive is not a regular file" >&2; exit 1; }

mode=$(stat -c '%a' "$ARCHIVE")
[[ "$mode" == "600" ]] || { echo "FAIL: archive permissions must be 600" >&2; exit 1; }

gzip -t "$ARCHIVE"
entries=$(tar -tzf "$ARCHIVE")

if printf '%s\n' "$entries" | grep -Eq '(^/|(^|/)(\.\.?)(/|$)|(^|/)\.env([.]|$)|(^|/)\.git(/|$)|(^|/)(db\.sqlite3|.*\.dump|.*\.backup|.*\.bak)(/|$)|(^|/)(secret|secrets|credential|credentials|token|tokens|private[_-]?key)(/|$))'; then
  echo "FAIL: archive contains a prohibited path" >&2
  exit 1
fi

types=$(tar -tvzf "$ARCHIVE")
if printf '%s\n' "$types" | awk 'NF && substr($0,1,1) !~ /^[-d]$/ {bad=1} END {exit bad}'; then
  :
else
  echo "FAIL: archive contains a non-regular/non-directory entry" >&2
  exit 1
fi

count=$(printf '%s\n' "$entries" | sed '/^$/d' | wc -l | tr -d ' ')
[[ "$count" -gt 0 ]] || { echo "FAIL: archive contains no entries" >&2; exit 1; }

echo "PASS: persistent-asset archive verified; entries=$count"
