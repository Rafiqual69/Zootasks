"""Deterministic binding between runtime incidents and governance evidence.

This is an evidence-correlator, not an authorization engine. It requires the
runtime decision, policy bundle, incident and release evidence to agree on
identity and release context before a recovery path can be trusted.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import re

from core.ai_incident_response import IncidentEvidence, IncidentResponseError, incident_digest
from core.ai_policy_evidence_bundle import PolicyEvidenceBundle, bundle_digest
from core.ai_release_tevv_gate import ReleaseEvidence, release_digest
from core.ai_runtime_monitor import RuntimeDecision, RuntimeMonitorError, verify_runtime_decision_context

class IncidentEvidenceBindingError(ValueError):
    pass

@dataclass(frozen=True)
class IncidentEvidenceBinding:
    incident_digest: str
    policy_bundle_digest: str
    release_digest: str
    runtime_decision_digest: str
    binding_digest: str

def bind_incident_evidence(
    incident: IncidentEvidence,
    policy_bundle: PolicyEvidenceBundle,
    release: ReleaseEvidence,
    runtime_decision: RuntimeDecision,
    *,
    expected_incident_digest: str,
    expected_policy_bundle_digest: str,
    expected_release_digest: str,
) -> IncidentEvidenceBinding:
    try:
        actual_incident = incident_digest(incident)
    except IncidentResponseError as exc:
        raise IncidentEvidenceBindingError(str(exc)) from exc
    actual_policy = bundle_digest(policy_bundle)
    actual_release = release_digest(release)

    if actual_incident != expected_incident_digest:
        raise IncidentEvidenceBindingError("incident_digest_mismatch")
    if actual_policy != expected_policy_bundle_digest:
        raise IncidentEvidenceBindingError("policy_bundle_digest_mismatch")
    if actual_release != expected_release_digest:
        raise IncidentEvidenceBindingError("release_digest_mismatch")
    if incident.system_id != release.system_id or incident.release_id != release.release_id:
        raise IncidentEvidenceBindingError("incident_release_identity_mismatch")
    runtime_digest = incident.runtime_decision_digest
    if not re.fullmatch(r"[0-9a-f]{64}", runtime_digest):
        raise IncidentEvidenceBindingError("runtime_decision_digest_invalid")
    try:
        verify_runtime_decision_context(incident.system_id, incident.release_id, runtime_decision)
    except RuntimeMonitorError as exc:
        raise IncidentEvidenceBindingError(str(exc)) from exc
    if runtime_decision.decision_digest != incident.runtime_decision_digest:
        raise IncidentEvidenceBindingError("runtime_decision_digest_mismatch")
    if policy_bundle.decision == "allow":
        raise IncidentEvidenceBindingError("incident_binding_allow_bundle_forbidden")

    payload = {
        "incident_digest": actual_incident,
        "policy_bundle_digest": actual_policy,
        "release_digest": actual_release,
        "runtime_decision_digest": incident.runtime_decision_digest,
    }
    digest = sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return IncidentEvidenceBinding(
        actual_incident, actual_policy, actual_release,
        incident.runtime_decision_digest, digest,
    )
