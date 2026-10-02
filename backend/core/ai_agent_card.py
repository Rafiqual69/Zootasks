"""Protocol-neutral, fail-closed Agent/Provider Card validation.

Cards describe capabilities; they never grant authorization or credentials.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Mapping

class AgentCardError(ValueError):
    pass

@dataclass(frozen=True)
class AgentCard:
    agent_id: str
    provider_id: str
    version: str
    protocols: tuple[str, ...]
    capabilities: tuple[str, ...]
    data_classes: tuple[str, ...] = ()
    destinations: tuple[str, ...] = ()
    signature: str | None = None

def _require_text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AgentCardError(name + "_required")
    return value.strip()

def parse_agent_card(payload: Mapping[str, Any]) -> AgentCard:
    if not isinstance(payload, Mapping):
        raise AgentCardError("card_invalid")
    allowed={"agent_id","provider_id","version","protocols","capabilities","data_classes","destinations","signature"}
    if set(payload)-allowed:
        raise AgentCardError("card_unknown_field")
    agent_id=_require_text(payload.get("agent_id"),"agent_id")
    provider_id=_require_text(payload.get("provider_id"),"provider_id")
    version=_require_text(payload.get("version"),"version")
    protocols=tuple(sorted(set(payload.get("protocols", ()))))
    capabilities=tuple(sorted(set(payload.get("capabilities", ()))))
    data_classes=tuple(sorted(set(payload.get("data_classes", ()))))
    destinations=tuple(sorted(set(payload.get("destinations", ()))))
    if not protocols or not capabilities:
        raise AgentCardError("card_capabilities_required")
    if any(not isinstance(x,str) or not x.strip() for x in protocols+capabilities+data_classes+destinations):
        raise AgentCardError("card_list_value_invalid")
    signature=payload.get("signature")
    if signature is not None and (not isinstance(signature,str) or not signature.strip()):
        raise AgentCardError("card_signature_invalid")
    return AgentCard(agent_id,provider_id,version,protocols,capabilities,data_classes,destinations,signature)

def card_digest(card: AgentCard) -> str:
    payload={k:getattr(card,k) for k in ("agent_id","provider_id","version","protocols","capabilities","data_classes","destinations","signature")}
    return sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def is_signed(card: AgentCard) -> bool:
    return bool(card.signature)
