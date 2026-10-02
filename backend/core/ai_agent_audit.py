"""Deterministic, data-minimized provenance receipts for AI agent decisions."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

AUDIT_SCHEMA_VERSION = "1.0"


class AIAuditError(ValueError):
    """Raised when an AI provenance receipt cannot be safely created."""


_ALLOWED_FIELDS = frozenset({
    "agent_id",
    "capability_id",
    "correlation_id",
    "data_class",
    "policy_version",
    "decision",
    "tool_class",
    "tool_decision",
    "evidence_reference",
})


def build_provenance_receipt(event: Mapping[str, Any]) -> dict[str, str]:
    """Return a deterministic receipt without copying prompts, secrets, or outputs."""
    unknown = set(event) - _ALLOWED_FIELDS
    if unknown:
        raise AIAuditError("ai_audit_unknown_field")

    required = ("agent_id", "capability_id", "correlation_id", "decision")
    if any(not str(event.get(key, "")).strip() for key in required):
        raise AIAuditError("ai_audit_required_field_missing")

    safe = {key: str(event[key]) for key in sorted(event)}
    canonical = json.dumps(
        {"schema_version": AUDIT_SCHEMA_VERSION, **safe},
        sort_keys=True,
        separators=(",", ":"),
    )
    return {
        "schema_version": AUDIT_SCHEMA_VERSION,
        **safe,
        "receipt_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
    }
