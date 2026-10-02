"""Deterministic source attestation and privacy gate.

This layer records trust evidence without treating a signature as blanket
authorization. It is network-free and does not verify cryptographic keys.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json

class SourceAttestationError(ValueError):
    pass

@dataclass(frozen=True)
class SourceManifest:
    source_id: str
    provider_id: str
    version: str
    source_type: str
    regions: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    attestation_ref: str | None = None
    status: str = "unverified"

@dataclass(frozen=True)
class AttestationDecision:
    state: str
    manifest_digest: str
    reasons: tuple[str, ...]

def validate_manifest(m: SourceManifest) -> None:
    if not m.source_id.strip() or not m.provider_id.strip() or not m.version.strip():
        raise SourceAttestationError("manifest_identity_required")
    if m.status not in {"unverified","attested","revoked"}:
        raise SourceAttestationError("manifest_status_invalid")
    if not m.regions or not m.evidence_refs:
        raise SourceAttestationError("manifest_evidence_required")
    if m.status == "attested" and not m.attestation_ref:
        raise SourceAttestationError("attestation_reference_required")
    if any(not x.strip() for x in m.regions+m.evidence_refs):
        raise SourceAttestationError("manifest_list_invalid")

def manifest_digest(m: SourceManifest) -> str:
    validate_manifest(m)
    payload={k:getattr(m,k) for k in ("source_id","provider_id","version","source_type","regions","evidence_refs","attestation_ref","status")}
    return sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def evaluate_manifest(m: SourceManifest) -> AttestationDecision:
    digest=manifest_digest(m)
    if m.status == "revoked":
        return AttestationDecision("quarantined",digest,("source_revoked",))
    if m.status != "attested":
        return AttestationDecision("quarantined",digest,("source_not_attested",))
    return AttestationDecision("candidate",digest,("attestation_evidence_present",))
