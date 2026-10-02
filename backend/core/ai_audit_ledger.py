"""Tamper-evident, network-free audit ledger for AI decisions and actions."""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json

class AuditLedgerError(ValueError):
    pass

@dataclass(frozen=True)
class AuditEntry:
    sequence: int
    event_id: str
    actor_id: str
    action: str
    authorization_digest: str
    source_digest: str
    input_digest: str
    result_digest: str
    timestamp: str
    previous_digest: str | None = None

def entry_digest(entry: AuditEntry) -> str:
    payload={k:getattr(entry,k) for k in (
        "sequence","event_id","actor_id","action","authorization_digest",
        "source_digest","input_digest","result_digest","timestamp","previous_digest")}
    return sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def verify_ledger(entries: tuple[AuditEntry, ...]) -> str:
    if not entries:
        raise AuditLedgerError("audit_ledger_empty")
    previous=None
    for index, entry in enumerate(entries):
        if entry.sequence != index:
            raise AuditLedgerError("audit_sequence_invalid")
        if not entry.event_id.strip() or not entry.actor_id.strip() or not entry.action.strip():
            raise AuditLedgerError("audit_identity_required")
        if not entry.authorization_digest or not entry.source_digest or not entry.input_digest or not entry.result_digest:
            raise AuditLedgerError("audit_digest_fields_required")
        if index == 0:
            if entry.previous_digest is not None:
                raise AuditLedgerError("audit_root_parent_invalid")
        elif entry.previous_digest != previous:
            raise AuditLedgerError("audit_chain_break")
        previous=entry_digest(entry)
    return previous
