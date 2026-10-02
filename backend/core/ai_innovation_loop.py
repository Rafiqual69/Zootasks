"""Safe autonomous innovation loop for ZooTasks AI capabilities."""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import FrozenSet

class InnovationGateError(ValueError): pass
FORBIDDEN_ACTIONS: FrozenSet[str] = frozenset({"wallet_mutation","withdrawal_approval","withdrawal_payment","promotion_payout","permission_change","owner_authentication","identity_binding","production_activation","external_side_effect"})
@dataclass(frozen=True)
class InnovationProposal:
    proposal_id: str
    capability_id: str
    objective: str
    mechanism: str
    evidence_refs: tuple[str, ...]
    affected_boundaries: tuple[str, ...]
    requested_actions: FrozenSet[str]
    novelty_basis: tuple[str, ...]
    reversibility: str
    human_approval_required: bool = True
@dataclass(frozen=True)
class InnovationDecision:
    state: str
    proposal_digest: str
    reasons: tuple[str, ...]
def proposal_digest(proposal: InnovationProposal) -> str:
    payload = {"proposal_id":proposal.proposal_id,"capability_id":proposal.capability_id,"objective":proposal.objective,"mechanism":proposal.mechanism,"evidence_refs":proposal.evidence_refs,"affected_boundaries":proposal.affected_boundaries,"requested_actions":sorted(proposal.requested_actions),"novelty_basis":proposal.novelty_basis,"reversibility":proposal.reversibility,"human_approval_required":proposal.human_approval_required}
    return sha256(json.dumps(payload, sort_keys=True, separators=(",",":")).encode()).hexdigest()
def evaluate_innovation(proposal: InnovationProposal, known_mechanisms: FrozenSet[str]) -> InnovationDecision:
    reasons=[]
    if not proposal.proposal_id.strip() or not proposal.capability_id.strip(): reasons.append("identity_required")
    if not proposal.objective.strip() or not proposal.mechanism.strip(): reasons.append("objective_and_mechanism_required")
    if not proposal.evidence_refs: reasons.append("evidence_required")
    if not proposal.novelty_basis: reasons.append("novelty_evidence_required")
    if proposal.mechanism.casefold() in {m.casefold() for m in known_mechanisms}: reasons.append("mechanism_already_known")
    if proposal.reversibility not in {"reversible","staged","read_only"}: reasons.append("unsafe_reversibility_class")
    if proposal.requested_actions.intersection(FORBIDDEN_ACTIONS): reasons.append("forbidden_action_requested")
    if not proposal.human_approval_required: reasons.append("human_approval_required")
    if reasons: return InnovationDecision("quarantined", proposal_digest(proposal), tuple(reasons))
    return InnovationDecision("candidate", proposal_digest(proposal), ("novelty_candidate",))
def promote_innovation_candidate(decision: InnovationDecision, approved: bool) -> InnovationDecision:
    if decision.state != "candidate": raise InnovationGateError("innovation_not_promotable")
    if not approved: raise InnovationGateError("innovation_human_approval_required")
    return InnovationDecision("approved_for_design_review", decision.proposal_digest, ("approved_for_design_review",))