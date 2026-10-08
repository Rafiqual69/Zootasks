"""Fail-closed trust boundary for ZooTasks inter-agent requests.
AI agents are peers across a trust boundary. A receiving executor must not trust upstream authorization claims.
"""
from __future__ import annotations
import hashlib, hmac, json, os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping
from django.core.cache import cache

class AIAgentTrustError(PermissionError):
    """Raised when an inter-agent request fails the trust boundary."""

MAX_CLOCK_SKEW_SECONDS = 30
MAX_TTL_SECONDS = 300
MIN_TRUST_KEY_BYTES = 32
NONCE_PREFIX = "zootasks:ai-agent-nonce:"

_FORBIDDEN_CLAIM_KEY_PARTS = (
    "password", "secret", "token", "private_key", "credential",
    "authorization", "access_key", "api_key", "session", "cookie",
    "bank_account", "payment_identifier",
)


def _validate_claims(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if not isinstance(key, str) or not key:
                raise AIAgentTrustError("Invalid AI agent claim key.")
            lowered = key.casefold()
            if any(part in lowered for part in _FORBIDDEN_CLAIM_KEY_PARTS):
                raise AIAgentTrustError("Sensitive AI agent claim key forbidden.")
            _validate_claims(nested)
        return
    if isinstance(value, (list, tuple)):
        for nested in value:
            _validate_claims(nested)
        return
    if value is None or isinstance(value, (str, bool, int)):
        return
    raise AIAgentTrustError("Invalid AI agent claim value.")

@dataclass(frozen=True)
class AIAgentRequest:
    sender: str
    receiver: str
    request_id: str
    request_digest: str
    nonce: str
    issued_at: int
    expires_at: int
    claims: Mapping[str, Any]
    signature: str

def _trust_key() -> bytes:
    raw = os.environ.get("AI_AGENT_TRUST_KEY", "")
    if not raw:
        raise AIAgentTrustError("AI agent trust key is not configured.")
    key = raw.encode("utf-8")
    if len(key) < MIN_TRUST_KEY_BYTES:
        raise AIAgentTrustError("AI agent trust key is too short.")
    return key

def _canonical_payload(request: AIAgentRequest) -> bytes:
    values = {"sender": request.sender, "receiver": request.receiver, "request_id": request.request_id, "request_digest": request.request_digest, "nonce": request.nonce, "issued_at": request.issued_at, "expires_at": request.expires_at, "claims": dict(request.claims)}
    return json.dumps(values, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def sign_inter_agent_request(request: AIAgentRequest) -> str:
    """Create a detached HMAC signature; the secret never enters the envelope."""
    unsigned = AIAgentRequest(request.sender, request.receiver, request.request_id, request.request_digest, request.nonce, request.issued_at, request.expires_at, request.claims, "")
    return hmac.new(_trust_key(), _canonical_payload(unsigned), hashlib.sha256).hexdigest()

def verify_inter_agent_request(request: AIAgentRequest, *, expected_receiver: str, now: int | None = None) -> None:
    """Authenticate and consume an inter-agent request exactly once.

    This verifies message integrity only; the receiver must independently invoke
    the normal policy/execution authorization layer before any protected action.
    """
    if not isinstance(request, AIAgentRequest):
        raise AIAgentTrustError("Malformed AI agent request.")
    if not isinstance(expected_receiver, str) or not expected_receiver.strip():
        raise AIAgentTrustError("Invalid receiver.")
    if request.receiver != expected_receiver:
        raise AIAgentTrustError("AI agent audience mismatch.")
    if not request.sender or request.sender == request.receiver:
        raise AIAgentTrustError("Invalid AI agent sender.")
    if not request.request_id or not request.request_digest or not request.nonce:
        raise AIAgentTrustError("Incomplete AI agent request binding.")
    if not isinstance(request.claims, Mapping):
        raise AIAgentTrustError("Invalid AI agent claims.")
    _validate_claims(request.claims)
    if not isinstance(request.issued_at, int) or not isinstance(request.expires_at, int):
        raise AIAgentTrustError("Invalid AI agent timestamps.")
    current = int(datetime.now(timezone.utc).timestamp()) if now is None else now
    if request.expires_at <= request.issued_at or request.expires_at - request.issued_at > MAX_TTL_SECONDS:
        raise AIAgentTrustError("Invalid AI agent expiry.")
    if current < request.issued_at - MAX_CLOCK_SKEW_SECONDS or current > request.expires_at + MAX_CLOCK_SKEW_SECONDS:
        raise AIAgentTrustError("AI agent request outside validity window.")
    expected = sign_inter_agent_request(request)
    if not hmac.compare_digest(expected, request.signature):
        raise AIAgentTrustError("AI agent request signature invalid.")
    if request.claims.get("authorized") is True or request.claims.get("approved") is True:
        raise AIAgentTrustError("Upstream authorization claims are not trusted.")
    cache_key = f"{NONCE_PREFIX}{request.receiver}:{request.nonce}"
    if not cache.add(cache_key, "consumed", timeout=max(1, request.expires_at - current)):
        raise AIAgentTrustError("AI agent request replay detected.")
