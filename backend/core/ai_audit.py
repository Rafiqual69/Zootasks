"""Secret-free structured metadata for AI security decisions."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any
from .ai_action_risk import AIRiskLevel

class AIDataTrust(StrEnum):
    INSTRUCTION = "instruction"
    UNTRUSTED_DATA = "untrusted_data"
    TOOL_OUTPUT = "tool_output"
    MEMORY = "memory"

@dataclass(frozen=True)
class AIAuditEvent:
    request_digest: str
    decision: str
    risk: AIRiskLevel
    tool: str
    action: str
    target: str
    scope: str
    policy_version: str
    data_trust: AIDataTrust

    def to_safe_dict(self) -> dict[str, Any]:
        """Return bounded metadata; payloads, prompts, secrets and PII are excluded."""
        values = asdict(self)
        values["risk"] = self.risk.value
        values["data_trust"] = self.data_trust.value
        return values

def build_ai_audit_event(*, request_digest: str, decision: str, risk: AIRiskLevel, tool: str, action: str, target: str, scope: str, policy_version: str, data_trust: AIDataTrust) -> AIAuditEvent:
    fields = (request_digest, decision, tool, action, target, scope, policy_version)
    if not all(isinstance(value, str) and value.strip() for value in fields):
        raise ValueError("AI audit metadata must use non-empty strings.")
    if len(request_digest) != 64:
        raise ValueError("AI audit digest must be SHA-256 sized.")
    if not isinstance(risk, AIRiskLevel) or not isinstance(data_trust, AIDataTrust):
        raise ValueError("Invalid AI audit classification.")
    return AIAuditEvent(request_digest, decision, risk, tool, action, target, scope, policy_version, data_trust)
