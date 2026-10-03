"""Cryptographic integrity helpers for AI evaluation evidence.

The digest is computed from canonical JSON with integrity fields excluded.
This makes the evidence self-verifiable without introducing a signing key.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def evidence_integrity_payload(evidence: dict) -> dict:
    payload = dict(evidence)
    payload.pop("integrity", None)
    return payload


def evidence_sha256(evidence: dict) -> str:
    return sha256_json(evidence_integrity_payload(evidence))
