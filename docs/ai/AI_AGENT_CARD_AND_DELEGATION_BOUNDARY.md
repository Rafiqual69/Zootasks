# AI Agent Card & Delegation Boundary

## Research basis

NIST's 2026 agent identity work focuses on identification, authentication, authorization, auditing, non-repudiation and controls against prompt injection. A2A 1.0 defines Agent Cards containing identity, capabilities, security requirements and skills, and permits signed cards; its security model requires authorization scoped to the authenticated caller. citeturn0search3turn0search0

## ZooTasks model

ZooTasks treats an Agent/Provider Card as a **capability declaration**, never as permission. Cards are normalized into a protocol-neutral form so A2A, MCP-style or future protocols can sit behind the same security boundary.

A card may describe:
- agent and provider identity
- version
- supported protocols
- capabilities
- data classes
- allowed destinations
- optional signature/attestation

Sensitive credentials are never stored in the card.

## Delegation

Multi-agent work uses a deterministic scoped delegation statement containing:
- issuer agent
- subject agent
- exact actions
- exact tools
- allowed destinations
- bounded call budget
- expiry
- optional approval reference

Delegation is deny-by-default. Critical financial, identity, permission, production-activation and external-side-effect actions are forbidden even if a caller attempts to add them to a scope.

Delegation does not mint credentials, send requests, or bypass provider authorization. Actual credential acquisition remains an external authorized control-plane operation.

## Controlled flow

`discover card -> validate card -> verify provider/source -> compare capability genome -> quarantine -> authorize scoped delegation -> deterministic execution gate -> audit -> circuit breaker`

This keeps interoperability separate from authority and keeps provenance separate from trust.
