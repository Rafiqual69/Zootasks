"""Fail-closed AI incident evidence and safe rollback state machine.

The state machine records and authorizes *state transitions only*. It never
executes rollback, decommissioning, deployment, or business/financial actions.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
import json
import re

class IncidentResponseError(ValueError):
    pass

STATES = frozenset({
    "detected",
    "quarantined",
    "rollback_candidate",
    "rollback_approved",
    "rolled_back",
    "revalidation_required",
    "recovered",
    "decommissioned",
})

TERMINAL_STATES = frozenset({"recovered", "decommissioned"})

@dataclass(frozen=True)
class IncidentEvidence:
    incident_id: str
    system_id: str
    release_id: str
    severity: str
    detection_reason: str
    runtime_decision_digest: str
    state: str = "detected"
    approval_ref: str | None = None
    rollback_ref: str | None = None
    revalidation_ref: str | None = None

def _validate(e: IncidentEvidence) -> None:
    required = (
        e.incident_id, e.system_id, e.release_id, e.severity,
        e.detection_reason, e.runtime_decision_digest,
    )
    if any(not str(value).strip() for value in required):
        raise IncidentResponseError("incident_evidence_required")
    if not re.fullmatch(r"[0-9a-f]{64}", e.runtime_decision_digest):
        raise IncidentResponseError("runtime_decision_digest_invalid")
    if e.state not in STATES:
        raise IncidentResponseError("incident_state_invalid")
    if e.severity not in {"low", "medium", "high", "critical"}:
        raise IncidentResponseError("incident_severity_invalid")
    for name in ("approval_ref", "rollback_ref", "revalidation_ref"):
        value = getattr(e, name)
        if value is not None and not value.strip():
            raise IncidentResponseError(f"{name}_invalid")

def incident_digest(e: IncidentEvidence) -> str:
    _validate(e)
    payload = {
        "incident_id": e.incident_id,
        "system_id": e.system_id,
        "release_id": e.release_id,
        "severity": e.severity,
        "detection_reason": e.detection_reason,
        "runtime_decision_digest": e.runtime_decision_digest,
        "state": e.state,
        "approval_ref": e.approval_ref,
        "rollback_ref": e.rollback_ref,
        "revalidation_ref": e.revalidation_ref,
    }
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def transition_incident(
    incident: IncidentEvidence,
    target_state: str,
    *,
    approval_ref: str | None = None,
    rollback_ref: str | None = None,
    revalidation_ref: str | None = None,
) -> IncidentEvidence:
    _validate(incident)
    if target_state not in STATES:
        raise IncidentResponseError("incident_target_state_invalid")
    if incident.state in TERMINAL_STATES:
        raise IncidentResponseError("incident_terminal_state")

    allowed = {
        "detected": {"quarantined"},
        "quarantined": {"rollback_candidate", "decommissioned"},
        "rollback_candidate": {"rollback_approved", "quarantined"},
        "rollback_approved": {"rolled_back"},
        "rolled_back": {"revalidation_required"},
        "revalidation_required": {"recovered", "quarantined"},
    }
    if target_state not in allowed.get(incident.state, set()):
        raise IncidentResponseError("incident_transition_denied")

    if target_state in {"rollback_approved", "decommissioned", "recovered"}:
        if not approval_ref and not incident.approval_ref:
            raise IncidentResponseError("incident_approval_required")

    if target_state == "rolled_back":
        if not rollback_ref and not incident.rollback_ref:
            raise IncidentResponseError("rollback_reference_required")

    if target_state == "recovered":
        if not revalidation_ref and not incident.revalidation_ref:
            raise IncidentResponseError("revalidation_reference_required")

    return replace(
        incident,
        state=target_state,
        approval_ref=approval_ref or incident.approval_ref,
        rollback_ref=rollback_ref or incident.rollback_ref,
        revalidation_ref=revalidation_ref or incident.revalidation_ref,
    )
