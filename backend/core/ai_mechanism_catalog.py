"""Deterministic mechanism catalog for safe innovation novelty checks."""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Iterable
from .ai_innovation_genome import InnovationGenome, genome_fingerprint

class MechanismCatalogError(ValueError):
    pass

@dataclass(frozen=True)
class MechanismRecord:
    mechanism_id: str
    name: str
    genome: InnovationGenome
    evidence_refs: tuple[str, ...] = ()
    status: str = "active"
    def __post_init__(self):
        if not self.mechanism_id.strip() or not self.name.strip():
            raise MechanismCatalogError("mechanism_identity_required")
        if self.status not in {"active", "deprecated"}:
            raise MechanismCatalogError("mechanism_status_invalid")
        if any(not ref.strip() for ref in self.evidence_refs):
            raise MechanismCatalogError("mechanism_evidence_ref_invalid")

@dataclass(frozen=True)
class CatalogDecision:
    state: str
    fingerprint: str
    matched_mechanism_id: str | None
    reasons: tuple[str, ...]

def catalog_fingerprint(records: Iterable[MechanismRecord]) -> str:
    payload = [{
        "mechanism_id": r.mechanism_id,
        "genome": genome_fingerprint(r.genome),
        "status": r.status,
        "evidence_refs": sorted(set(r.evidence_refs)),
    } for r in records]
    payload.sort(key=lambda item: item["mechanism_id"])
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def evaluate_against_catalog(genome: InnovationGenome, records: Iterable[MechanismRecord]) -> CatalogDecision:
    records = tuple(records)
    fp = genome_fingerprint(genome)
    for record in records:
        if genome_fingerprint(record.genome) == fp:
            return CatalogDecision("known", fp, record.mechanism_id, ("exact_mechanism_match",))
    return CatalogDecision("candidate", fp, None, ("no_exact_mechanism_match",))
