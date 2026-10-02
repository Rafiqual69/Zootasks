"""Fail-closed acquisition lifecycle for authorized ZooTasks outreach."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import FrozenSet

class AcquisitionGateError(ValueError): pass
STATES: FrozenSet[str]=frozenset({"discovered","research_verified","draft_ready","awaiting_owner_approval","approved","sent","provider_response","accepted","rejected","expired","quarantined"})
EXTERNAL_ACTION_STATES=frozenset({"sent"})

@dataclass(frozen=True)
class AcquisitionProposal:
    proposal_id:str
    provider_id:str
    purpose:str
    channel:str
    material_parameters:tuple[tuple[str,str],...]
    evidence_refs:tuple[str,...]
    state:str="draft_ready"

@dataclass(frozen=True)
class AcquisitionApproval:
    proposal_digest:str
    actor_id:str
    scope:str
    expires_at:str

def proposal_digest(proposal:AcquisitionProposal)->str:
    payload={"proposal_id":proposal.proposal_id,"provider_id":proposal.provider_id,"purpose":proposal.purpose,"channel":proposal.channel,"material_parameters":proposal.material_parameters,"evidence_refs":proposal.evidence_refs}
    return sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def _expiry(value:str)->datetime:
    try: result=datetime.fromisoformat(value.replace("Z","+00:00"))
    except ValueError as exc: raise AcquisitionGateError("approval_expiry_invalid") from exc
    if result.tzinfo is None: raise AcquisitionGateError("approval_expiry_timezone_required")
    return result.astimezone(timezone.utc)

def validate_proposal(proposal:AcquisitionProposal)->None:
    if not proposal.proposal_id.strip() or not proposal.provider_id.strip(): raise AcquisitionGateError("proposal_identity_required")
    if not proposal.purpose.strip() or not proposal.channel.strip(): raise AcquisitionGateError("proposal_details_required")
    if proposal.state not in STATES: raise AcquisitionGateError("proposal_state_invalid")
    if not proposal.evidence_refs: raise AcquisitionGateError("proposal_evidence_required")
    if any(not k.strip() or not v.strip() for k,v in proposal.material_parameters): raise AcquisitionGateError("material_parameters_invalid")

def authorize_transition(proposal:AcquisitionProposal,target_state:str,approval:AcquisitionApproval|None=None,now:datetime|None=None)->AcquisitionProposal:
    validate_proposal(proposal)
    if target_state not in STATES: raise AcquisitionGateError("target_state_invalid")
    if proposal.state in {"quarantined","expired","rejected","accepted"}: raise AcquisitionGateError("terminal_state")
    if target_state in EXTERNAL_ACTION_STATES:
        if approval is None: raise AcquisitionGateError("external_action_approval_required")
        if approval.proposal_digest!=proposal_digest(proposal): raise AcquisitionGateError("approval_proposal_digest_mismatch")
        if not approval.actor_id.strip() or not approval.scope.strip(): raise AcquisitionGateError("approval_identity_or_scope_required")
        if (now or datetime.now(timezone.utc)).astimezone(timezone.utc)>=_expiry(approval.expires_at): raise AcquisitionGateError("approval_expired")
    return AcquisitionProposal(proposal.proposal_id,proposal.provider_id,proposal.purpose,proposal.channel,proposal.material_parameters,proposal.evidence_refs,target_state)
