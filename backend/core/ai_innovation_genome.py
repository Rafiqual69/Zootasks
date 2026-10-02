"""Deterministic innovation fingerprint and novelty gate for ZooTasks."""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Iterable

class InnovationGenomeError(ValueError):
    pass

DIMENSIONS=("capability","workflow","integration","safety","worker_value")

@dataclass(frozen=True)
class InnovationGenome:
    capability: str
    workflow: str
    integration: str
    safety: str
    worker_value: str

    def __post_init__(self):
        if any(not str(getattr(self, d)).strip() for d in DIMENSIONS):
            raise InnovationGenomeError("all_genome_dimensions_required")

def genome_fingerprint(genome: InnovationGenome) -> str:
    payload={d:str(getattr(genome,d)).strip().casefold() for d in DIMENSIONS}
    return sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def _tokens(value: str) -> set[str]:
    return {t for t in value.casefold().replace("-", " ").replace("_", " ").split() if t}

def novelty_distance(candidate: InnovationGenome, known: Iterable[InnovationGenome]) -> int:
    known_list=tuple(known)
    c={d:_tokens(getattr(candidate,d)) for d in DIMENSIONS}
    if not known_list:
        return len(DIMENSIONS)
    return min(sum(c[d] != _tokens(getattr(item,d)) for d in DIMENSIONS) for item in known_list)

def evaluate_genome(candidate: InnovationGenome, known: Iterable[InnovationGenome]) -> tuple[str, tuple[str,...]]:
    known_list=tuple(known)
    fp=genome_fingerprint(candidate)
    if any(genome_fingerprint(k)==fp for k in known_list):
        return "known", ("exact_genome_match",)
    distance=novelty_distance(candidate,known_list)
    return "novel_candidate", (f"changed_dimensions:{distance}",)
