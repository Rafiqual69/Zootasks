"""Append-only provenance queue for untrusted discovery observations."""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Mapping

class ProvenanceQueueError(ValueError):
    pass

@dataclass(frozen=True)
class ProvenanceObservation:
    observation_id: str
    source_kind: str
    source_identifier: str
    observed_at: str
    content_digest: str
    previous_digest: str | None
    sequence: int
    trust_state: str = "untrusted"

@dataclass(frozen=True)
class ProvenanceDecision:
    status: str
    record: ProvenanceObservation
    record_digest: str

def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def content_digest(payload: Mapping[str, Any]) -> str:
    if not isinstance(payload, Mapping):
        raise ProvenanceQueueError("observation_payload_invalid")
    return sha256(_canonical(payload).encode("utf-8")).hexdigest()

def observation_digest(record: ProvenanceObservation) -> str:
    payload = {
        "observation_id": record.observation_id,
        "source_kind": record.source_kind,
        "source_identifier": record.source_identifier,
        "observed_at": record.observed_at,
        "content_digest": record.content_digest,
        "previous_digest": record.previous_digest,
        "sequence": record.sequence,
        "trust_state": record.trust_state,
    }
    return sha256(_canonical(payload).encode()).hexdigest()

def enqueue_observation(*, observation_id: str, source_kind: str, source_identifier: str,
                        observed_at: str, payload: Mapping[str, Any],
                        previous_digest: str | None = None, sequence: int = 1) -> ProvenanceDecision:
    if not observation_id.strip() or not source_kind.strip() or not source_identifier.strip():
        raise ProvenanceQueueError("observation_identity_required")
    if not observed_at.strip():
        raise ProvenanceQueueError("observation_timestamp_required")
    if sequence < 1:
        raise ProvenanceQueueError("observation_sequence_invalid")
    if previous_digest is not None and len(previous_digest) != 64:
        raise ProvenanceQueueError("previous_digest_invalid")
    record = ProvenanceObservation(
        observation_id=observation_id, source_kind=source_kind,
        source_identifier=source_identifier, observed_at=observed_at,
        content_digest=content_digest(payload), previous_digest=previous_digest,
        sequence=sequence,
    )
    return ProvenanceDecision("quarantined", record, observation_digest(record))
