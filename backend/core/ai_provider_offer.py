"""Fail-closed validation and normalization for provider-supplied AI offers."""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping

class AIProviderOfferError(ValueError):
    """Expected rejection of invalid or unsafe provider offer."""

ALLOWED_ROUTES=frozenset({"api_partner","public_offer","workforce_platform","enterprise_contract","manual_research"})
ALLOWED_AUTH=frozenset({"verified","pending","quarantined","revoked"})
ALLOWED_RISK=frozenset({"approved","review_required","quarantined","revoked"})
ALLOWED_SYNC=frozenset({"active","stale","failed","disabled"})
ALLOWED_SENSITIVITY=frozenset({"public","internal","personal","sensitive","restricted"})
ALLOWED_SOURCE_KINDS=frozenset({"url","api","feed","contract"})
ALLOWED_CATEGORIES=frozenset({"data_annotation","multimodal_evaluation","llm_evaluation","preference_ranking","prompt_evaluation","search_relevance","translation","ai_safety","agent_evaluation","data_collection","output_verification","human_review"})

@dataclass(frozen=True)
class CanonicalOffer:
    payload: dict[str,Any]
    @property
    def executable(self)->bool:
        return (self.payload["authorization"]["status"]=="verified"
                and self.payload["risk"]["state"]=="approved"
                and self.payload["sync"]["status"]=="active")

def _mapping(value:Any,name:str)->Mapping[str,Any]:
    if not isinstance(value,Mapping): raise AIProviderOfferError(f"offer_{name}_invalid")
    return value

def _string(value:Any,name:str,max_length:int=1000)->str:
    if not isinstance(value,str) or not value.strip() or len(value)>max_length: raise AIProviderOfferError(f"offer_{name}_invalid")
    return value.strip()

def _enum(value:Any,name:str,allowed:frozenset[str])->str:
    value=_string(value,name,200)
    if value not in allowed: raise AIProviderOfferError(f"offer_{name}_unsupported")
    return value

def _list(value:Any,name:str,max_items:int=200)->list[str]:
    if not isinstance(value,list) or len(value)>max_items or not all(isinstance(x,str) and x.strip() for x in value):
        raise AIProviderOfferError(f"offer_{name}_invalid")
    return [x.strip() for x in value]

def validate_and_normalize_offer(raw:Mapping[str,Any])->CanonicalOffer:
    if not isinstance(raw,Mapping): raise AIProviderOfferError("offer_root_invalid")
    allowed={"schema_version","offer_id","provider","authorization","source","eligibility","task","reward","data_policy","qualification","verification","adapter","sync","provenance","risk"}
    if set(raw)!=allowed: raise AIProviderOfferError("offer_root_fields_invalid")
    if raw["schema_version"]!="1.0": raise AIProviderOfferError("offer_schema_version_unsupported")

    p=_mapping(raw["provider"],"provider")
    provider={"provider_id":_string(p.get("provider_id"),"provider_id",128),"name":_string(p.get("name"),"provider_name",200)}

    a=_mapping(raw["authorization"],"authorization")
    auth_status=_enum(a.get("status"),"authorization_status",ALLOWED_AUTH)
    route=_enum(a.get("route"),"authorization_route",ALLOWED_ROUTES)
    contract=a.get("contract_reference")
    if contract is not None: contract=_string(contract,"contract_reference",200)

    s=_mapping(raw["source"],"source")
    source={"kind":_enum(s.get("kind"),"source_kind",ALLOWED_SOURCE_KINDS),"identifier":_string(s.get("identifier"),"source_identifier")}

    e=_mapping(raw["eligibility"],"eligibility")
    eligibility={"regions":sorted(set(_list(e.get("regions"),"regions"))),"languages":sorted(set(_list(e.get("languages"),"languages"))),"requirements":sorted(set(_list(e.get("requirements",[]),"requirements",50)))}

    t=_mapping(raw["task"],"task")
    task={"category":_enum(t.get("category"),"task_category",ALLOWED_CATEGORIES),"title":_string(t.get("title"),"task_title",300),"skills":sorted(set(_list(t.get("skills",[]),"skills",100)))}

    r=_mapping(raw["reward"],"reward")
    try: amount=Decimal(str(r.get("amount")))
    except (InvalidOperation,TypeError): raise AIProviderOfferError("offer_reward_amount_invalid")
    if amount<0: raise AIProviderOfferError("offer_reward_amount_invalid")
    currency=_string(r.get("currency"),"reward_currency",3)
    if len(currency)!=3 or currency!=currency.upper() or not currency.isalpha(): raise AIProviderOfferError("offer_reward_currency_invalid")
    reward={"amount":str(amount.normalize()),"currency":currency,"payment_terms":_string(r.get("payment_terms"),"payment_terms")}

    d=_mapping(raw["data_policy"],"data_policy")
    data_policy={"sensitivity":_enum(d.get("sensitivity"),"data_sensitivity",ALLOWED_SENSITIVITY),"retention":_string(d.get("retention"),"data_retention"),"processing_restrictions":sorted(set(_list(d.get("processing_restrictions",[]),"processing_restrictions",50)))}

    q=_mapping(raw["qualification"],"qualification")
    if not isinstance(q.get("required"),bool): raise AIProviderOfferError("offer_qualification_invalid")
    method=q.get("method")
    if method is not None: method=_string(method,"qualification_method",500)

    v=_mapping(raw["verification"],"verification")
    verification={"method":_string(v.get("method"),"verification_method",500)}

    ad=_mapping(raw["adapter"],"adapter")
    adapter={"adapter_id":_string(ad.get("adapter_id"),"adapter_id",128),"version":_string(ad.get("version"),"adapter_version",64)}

    sy=_mapping(raw["sync"],"sync")
    sync_status=_enum(sy.get("status"),"sync_status",ALLOWED_SYNC)
    last=sy.get("last_success_at")
    if last is not None: last=_string(last,"last_success_at",100)

    pr=_mapping(raw["provenance"],"provenance")
    provenance={"source_revision":_string(pr.get("source_revision"),"source_revision",200),"evidence_refs":sorted(set(_list(pr.get("evidence_refs",[]),"evidence_refs",100)))}

    risk=_mapping(raw["risk"],"risk")
    risk_state=_enum(risk.get("state"),"risk_state",ALLOWED_RISK)
    reason=risk.get("reason")
    if reason is not None: reason=_string(reason,"risk_reason",1000)

    payload={"schema_version":"1.0","offer_id":_string(raw.get("offer_id"),"offer_id",128),"provider":provider,
      "authorization":{"status":auth_status,"route":route,"contract_reference":contract},"source":source,
      "eligibility":eligibility,"task":task,"reward":reward,"data_policy":data_policy,
      "qualification":{"required":q["required"],"method":method},"verification":verification,
      "adapter":adapter,"sync":{"status":sync_status,"last_success_at":last},"provenance":provenance,
      "risk":{"state":risk_state,"reason":reason}}
    if auth_status!="verified" or risk_state!="approved" or sync_status!="active":
        payload["risk"]={"state":"quarantined","reason":reason or "authorization_or_sync_gate"}
    return CanonicalOffer(payload)
