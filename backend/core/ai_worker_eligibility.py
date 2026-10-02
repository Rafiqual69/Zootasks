"""Deterministic, fail-closed worker eligibility for canonical AI offers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet

from .ai_provider_offer import CanonicalOffer


@dataclass(frozen=True)
class WorkerEligibilityProfile:
    region: str
    languages: FrozenSet[str]
    skills: FrozenSet[str]
    completed_qualifications: FrozenSet[str] = frozenset()


@dataclass(frozen=True)
class EligibilityDecision:
    eligible: bool
    reasons: tuple[str, ...]


def _norm(values: FrozenSet[str]) -> FrozenSet[str]:
    return frozenset(value.strip().casefold() for value in values if isinstance(value, str) and value.strip())


def evaluate_worker_eligibility(
    offer: CanonicalOffer,
    profile: WorkerEligibilityProfile,
) -> EligibilityDecision:
    """Return eligibility only; this never accepts a task or mutates state."""
    reasons: list[str] = []
    if not offer.executable:
        reasons.append("offer_not_executable")

    region = profile.region.strip().casefold()
    regions = _norm(frozenset(offer.payload["eligibility"]["regions"]))
    if regions and region not in regions:
        reasons.append("region_not_eligible")

    worker_languages = _norm(profile.languages)
    required_languages = _norm(frozenset(offer.payload["eligibility"]["languages"]))
    if required_languages and not required_languages.intersection(worker_languages):
        reasons.append("language_not_eligible")

    worker_skills = _norm(profile.skills)
    required_skills = _norm(frozenset(offer.payload["task"].get("skills", [])))
    if required_skills and not required_skills.issubset(worker_skills):
        reasons.append("skills_missing")

    qualification = offer.payload["qualification"]
    if qualification["required"]:
        method = qualification.get("method")
        completed = _norm(profile.completed_qualifications)
        if not isinstance(method, str) or method.strip().casefold() not in completed:
            reasons.append("qualification_missing")

    return EligibilityDecision(not reasons, tuple(reasons))
