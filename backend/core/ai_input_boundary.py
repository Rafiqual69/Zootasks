"""Trust classification helpers for AI input boundaries.

External content is data, never authority. These helpers intentionally do not
try to decide whether text is malicious; authorization remains outside model context.
"""
from __future__ import annotations

from .ai_audit import AIDataTrust

def classify_ai_input(source: str) -> AIDataTrust:
    if not isinstance(source, str):
        raise ValueError("AI input source must be a string.")
    normalized = source.strip().casefold()
    mapping = {
        "instruction": AIDataTrust.INSTRUCTION,
        "untrusted_data": AIDataTrust.UNTRUSTED_DATA,
        "tool_output": AIDataTrust.TOOL_OUTPUT,
        "memory": AIDataTrust.MEMORY,
    }
    try:
        return mapping[normalized]
    except KeyError as exc:
        raise ValueError("Unknown AI input trust class.") from exc

def assert_data_never_authorizes(*, data_trust: AIDataTrust, requested_authority: str) -> None:
    """Reject attempts to derive execution authority from model-visible data."""
    if not isinstance(data_trust, AIDataTrust) or not isinstance(requested_authority, str):
        raise ValueError("Invalid AI trust-boundary input.")
    if data_trust is not AIDataTrust.INSTRUCTION and requested_authority.strip():
        raise PermissionError("Untrusted AI data cannot grant authority.")
