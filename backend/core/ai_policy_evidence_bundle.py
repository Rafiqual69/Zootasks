"""Deterministic policy-decision evidence bundle.

Binds authorization, provenance, privacy, delegation and audit evidence into
one verifiable digest. This is evidence, not an authorization grant.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json

class PolicyEvidenceError(ValueError):
    pass

@dataclass(frozen=True)
class PolicyEvidenceBundle:
    bundle_id: str
    policy_version: str
    authorization_digest: str
    delegation_digest: str
    source_digest: str
    privacy_digest: str
    audit_digest: str
    decision: str
    approval_ref: str | None = None

def bundle_digest(bundle: PolicyEvidenceBundle) -> str:
    fields=(
        "bundle_id","policy_version","authorization_digest","delegation_digest",
        "source_digest","privacy_digest","audit_digest","decision","approval_ref")
    payload={k:getattr(bundle,k) for k in fields}
    if any(not str(payload[k]).strip() for k in fields[:-1]):
        raise PolicyEvidenceError("evidence_bundle_fields_required")
    if bundle.decision not in {"allow","deny","quarantine","review"}:
        raise PolicyEvidenceError("evidence_bundle_decision_invalid")
    if bundle.decision == "allow" and not bundle.approval_ref:
        raise PolicyEvidenceError("allow_requires_approval_reference")
    return sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def verify_bundle(bundle: PolicyEvidenceBundle, expected_digest: str) -> bool:
    if not expected_digest or bundle_digest(bundle) != expected_digest:
        raise PolicyEvidenceError("evidence_bundle_digest_mismatch")
    return True
