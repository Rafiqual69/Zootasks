"""Fail-closed release gate binding code, evaluation and policy evidence."""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json

class ReleaseGateError(ValueError):
    pass

@dataclass(frozen=True)
class ReleaseEvidence:
    release_id: str
    system_id: str
    code_revision: str
    source_revision_digest: str
    evaluation_digest: str
    policy_bundle_digest: str
    test_digest: str
    rollback_ref: str
    monitoring_ref: str
    approval_ref: str | None = None
    state: str = "candidate"

def release_digest(e: ReleaseEvidence) -> str:
    fields=(
        "release_id","system_id","code_revision","source_revision_digest",
        "evaluation_digest","policy_bundle_digest","test_digest",
        "rollback_ref","monitoring_ref","approval_ref","state")
    payload={k:getattr(e,k) for k in fields}
    if any(not str(payload[k]).strip() for k in fields[:9]):
        raise ReleaseGateError("release_evidence_required")
    if e.state not in {"candidate","approved","rejected","quarantined"}:
        raise ReleaseGateError("release_state_invalid")
    if e.state == "approved" and not e.approval_ref:
        raise ReleaseGateError("release_approval_required")
    return sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def evaluate_release(e: ReleaseEvidence) -> tuple[str, str]:
    digest=release_digest(e)
    if e.state != "approved":
        return "quarantined", digest
    return "approved_for_controlled_rollout", digest
