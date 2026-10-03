"""Integrity and provenance helpers for AI evaluation evidence."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str | Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def canonical_json_bytes(value: dict) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def sha256_json(value: dict) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def git_revision() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def build_provenance(
    *,
    evidence: dict,
    dataset_path: str | Path,
    schema_path: str | Path,
) -> dict:
    return {
        "git_revision": git_revision(),
        "dataset_sha256": sha256_file(dataset_path),
        "schema_sha256": sha256_file(schema_path),
        "evidence_payload_sha256": sha256_json(evidence),
        "hash_algorithm": "SHA-256",
    }
