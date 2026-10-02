"""Fail-closed resource and provider health circuit breaker."""
from __future__ import annotations
from dataclasses import dataclass
from typing import FrozenSet

class CircuitBreakerError(ValueError): pass
STATES: FrozenSet[str]=frozenset({"closed","open","half_open"})
@dataclass(frozen=True)
class CircuitPolicy:
    max_failures:int=3
    max_calls:int=20
    max_external_effects:int=0
@dataclass(frozen=True)
class CircuitState:
    state:str="closed"
    failures:int=0
    calls:int=0
    external_effects:int=0

def validate_policy(policy:CircuitPolicy)->None:
    if not 1<=policy.max_failures<=100: raise CircuitBreakerError("max_failures_out_of_bounds")
    if not 1<=policy.max_calls<=1000: raise CircuitBreakerError("max_calls_out_of_bounds")
    if policy.max_external_effects!=0: raise CircuitBreakerError("external_effect_budget_must_be_zero")

def allow_call(policy:CircuitPolicy,state:CircuitState)->CircuitState:
    validate_policy(policy)
    if state.state not in STATES: raise CircuitBreakerError("state_invalid")
    if min(state.failures,state.calls,state.external_effects)<0: raise CircuitBreakerError("negative_counter")
    if state.external_effects>policy.max_external_effects: raise CircuitBreakerError("external_effect_budget_exceeded")
    if state.failures>=policy.max_failures or state.calls>=policy.max_calls:
        return CircuitState("open",state.failures,state.calls,state.external_effects)
    return state

def record_result(policy:CircuitPolicy,state:CircuitState,success:bool)->CircuitState:
    current=allow_call(policy,state)
    if current.state=="open": return current
    failures=0 if success else current.failures+1
    calls=current.calls+1
    next_state="open" if failures>=policy.max_failures or calls>=policy.max_calls else "closed"
    return CircuitState(next_state,failures,calls,current.external_effects)
