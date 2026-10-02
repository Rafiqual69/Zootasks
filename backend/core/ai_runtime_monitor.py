"""Fail-closed runtime monitoring and rollback gate for AI capabilities.

Design: Runtime Trust Sentinel (RTS) converts live observations into a deterministic
decision. It never activates AI or performs business/financial actions.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json

class RuntimeMonitorError(ValueError):
    pass

STATES=frozenset({"healthy","degraded","rollback_required","quarantined"})

@dataclass(frozen=True)
class RuntimePolicy:
    max_error_rate_pct: int = 5
    max_consecutive_failures: int = 3
    max_latency_ms: int = 5000
    max_drift_score: int = 20

@dataclass(frozen=True)
class RuntimeObservation:
    system_id: str
    release_id: str
    calls: int
    failures: int
    consecutive_failures: int
    latency_ms: int
    drift_score: int
    policy_violations: int = 0

@dataclass(frozen=True)
class RuntimeDecision:
    state: str
    reasons: tuple[str, ...]
    rollback_required: bool
    decision_digest: str

def _validate_policy(p: RuntimePolicy) -> None:
    if not 1 <= p.max_error_rate_pct <= 100: raise RuntimeMonitorError("error_rate_threshold_invalid")
    if not 1 <= p.max_consecutive_failures <= 100: raise RuntimeMonitorError("failure_threshold_invalid")
    if not 1 <= p.max_latency_ms <= 600000: raise RuntimeMonitorError("latency_threshold_invalid")
    if not 0 <= p.max_drift_score <= 100: raise RuntimeMonitorError("drift_threshold_invalid")

def _validate_observation(o: RuntimeObservation) -> None:
    if not o.system_id.strip() or not o.release_id.strip(): raise RuntimeMonitorError("identity_required")
    if o.calls < 0 or o.failures < 0 or o.consecutive_failures < 0: raise RuntimeMonitorError("negative_counter")
    if o.failures > o.calls: raise RuntimeMonitorError("failures_exceed_calls")
    if o.latency_ms < 0 or not 0 <= o.drift_score <= 100 or o.policy_violations < 0:
        raise RuntimeMonitorError("observation_value_invalid")
    if o.calls == 0 and o.failures: raise RuntimeMonitorError("failures_without_calls")

def runtime_decision(policy: RuntimePolicy, observation: RuntimeObservation) -> RuntimeDecision:
    _validate_policy(policy); _validate_observation(observation)
    reasons=[]
    error_rate=(observation.failures * 100) / observation.calls if observation.calls else 0
    if error_rate > policy.max_error_rate_pct: reasons.append("error_rate_exceeded")
    if observation.consecutive_failures >= policy.max_consecutive_failures: reasons.append("consecutive_failures_exceeded")
    if observation.latency_ms > policy.max_latency_ms: reasons.append("latency_exceeded")
    if observation.drift_score > policy.max_drift_score: reasons.append("drift_exceeded")
    if observation.policy_violations > 0: reasons.append("policy_violation_detected")
    state="rollback_required" if reasons else "healthy"
    payload={"system_id":observation.system_id,"release_id":observation.release_id,"state":state,"reasons":reasons}
    digest=sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return RuntimeDecision(state,tuple(reasons),bool(reasons),digest)

def verify_runtime_decision_context(system_id: str, release_id: str, decision: RuntimeDecision) -> bool:
    if not system_id.strip() or not release_id.strip():
        raise RuntimeMonitorError("identity_required")
    if decision.state not in {"healthy", "rollback_required"}:
        raise RuntimeMonitorError("decision_state_invalid")
    expected = sha256(json.dumps(
        {
            "system_id": system_id,
            "release_id": release_id,
            "state": decision.state,
            "reasons": list(decision.reasons),
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode()).hexdigest()
    if decision.decision_digest != expected:
        raise RuntimeMonitorError("decision_digest_mismatch")
    if decision.rollback_required != (decision.state == "rollback_required"):
        raise RuntimeMonitorError("decision_state_mismatch")
    return True

def enforce_runtime_gate(policy: RuntimePolicy, observation: RuntimeObservation) -> str:
    decision=runtime_decision(policy,observation)
    return "quarantined" if decision.rollback_required else "healthy"
