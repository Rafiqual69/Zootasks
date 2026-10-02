# AI Provider Ingress & Quarantine

## Purpose

All newly discovered provider/offer candidates enter a fail-closed quarantine
boundary before any executable task pool.

NIST AI RMF guidance calls for monitoring third-party resources and for
post-deployment monitoring, incident response, recovery, and change management.

## Ingress invariants

1. Discovery is not authorization.
2. Ingress is not activation.
3. A valid offer is still quarantined at ingress.
4. Invalid candidates are quarantined with a reason; raw candidate content is
   not returned by the decision object.
5. Ingress performs no network access, credential use, worker assignment,
   wallet mutation, withdrawal action, promotion payout, or external side effect.
6. A candidate digest is deterministic, allowing the same input to be identified
   without trusting mutable display metadata.
7. Release cannot be performed by this module. A later activation gate must
   independently verify provider registration, authorization, offer risk,
   sync health, and material-change status.

## Processing flow

discovery -> ingress validation -> quarantine -> provider verification ->
offer approval -> sync-health gate -> material-change gate -> executable pool

Any failed gate remains quarantined or disabled.

## Failure behavior

Malformed, unsupported, or unsafe candidates fail closed. A candidate that
contains a valid canonical offer is still forced to risk.state=quarantined.
This prevents a future discovery source or adapter from accidentally turning
its own output into executable work.

## Operational evidence

The ingress decision is deterministic and network-free. The candidate digest
can be linked to source revision/evidence references by a higher-level evidence
store without storing untrusted raw content in this security boundary.

Production provider activation remains disabled until approval, monitoring,
rollback, and privacy evidence gates are satisfied.
