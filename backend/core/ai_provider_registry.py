"""Fail-closed provider registry primitives."""
from __future__ import annotations
from dataclasses import dataclass
from typing import FrozenSet

class AIProviderRegistryError(ValueError):
    pass

ALLOWED_ROUTES=frozenset({"api_partner","public_offer","workforce_platform","enterprise_contract","manual_research"})
ALLOWED_STATUSES=frozenset({"pending","verified","suspended","revoked"})
ALLOWED_ADAPTER_STATES=frozenset({"disabled","ready","quarantined"})

@dataclass(frozen=True)
class ProviderRegistration:
    provider_id:str
    name:str
    route:str
    status:str
    adapter_id:str
    adapter_version:str
    allowed_regions:FrozenSet[str]
    capabilities:FrozenSet[str]
    adapter_state:str="disabled"

def validate_provider_registration(entry:ProviderRegistration)->ProviderRegistration:
    for name,value in {"provider_id":entry.provider_id,"name":entry.name,"adapter_id":entry.adapter_id,"adapter_version":entry.adapter_version}.items():
        if not isinstance(value,str) or not value.strip() or len(value)>200:
            raise AIProviderRegistryError(f"provider_{name}_invalid")
    if entry.route not in ALLOWED_ROUTES: raise AIProviderRegistryError("provider_route_unsupported")
    if entry.status not in ALLOWED_STATUSES: raise AIProviderRegistryError("provider_status_unsupported")
    if entry.adapter_state not in ALLOWED_ADAPTER_STATES: raise AIProviderRegistryError("provider_adapter_state_unsupported")
    if not isinstance(entry.allowed_regions,frozenset) or not all(isinstance(x,str) and x.strip() for x in entry.allowed_regions):
        raise AIProviderRegistryError("provider_regions_invalid")
    if not isinstance(entry.capabilities,frozenset) or not all(isinstance(x,str) and x.strip() for x in entry.capabilities):
        raise AIProviderRegistryError("provider_capabilities_invalid")
    if entry.status!="verified" and entry.adapter_state=="ready":
        raise AIProviderRegistryError("unverified_provider_cannot_be_ready")
    return entry

def can_sync_provider(entry:ProviderRegistration)->bool:
    validate_provider_registration(entry)
    return entry.status=="verified" and entry.adapter_state=="ready"
