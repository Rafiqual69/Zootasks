# AI Incident Response and Safe Rollback State Machine

ZooTasks treats runtime monitoring as a detection signal, not as permission to
execute a rollback. The incident state machine records evidence and permits
only explicitly valid, fail-closed transitions.

## Lifecycle

`detected → quarantined → rollback_candidate → rollback_approved → rolled_back → revalidation_required → recovered`

A quarantined incident may instead enter `decommissioned` when the system is
no longer suitable for continued operation. Terminal states cannot transition
again.

## Security properties

- Runtime decision digest binds the incident to the exact RTS decision.
- System and release identity are mandatory.
- Invalid states and transitions fail closed.
- Approval is required before rollback approval, decommissioning, and recovery.
- A rollback reference is required before a rollback can be recorded as complete.
- A revalidation reference is required before recovery.
- The module records state; it does **not** execute rollback, deployment,
  decommissioning, wallet mutation, withdrawal approval/payment, promotion
  payout, permission changes, or owner authentication.
- Incident evidence remains compatible with the existing tamper-evident audit
  ledger and policy evidence bundle.

## Why this design

NIST AI RMF guidance calls for documented incident response, recovery,
monitoring, deactivation/decommissioning, preservation of forensic material,
root-cause review, and criteria for redeployment. NIST also emphasizes that
post-deployment monitoring exposes real-world behavior not fully captured by
pre-deployment evaluation. ZooTasks therefore separates:

1. **Detection** — RTS identifies a threshold breach.
2. **Containment** — quarantine prevents continued trusted operation.
3. **Decision** — an authorized actor approves a rollback/decommission path.
4. **Recovery evidence** — the rollback and revalidation artifacts are recorded.
5. **Return to service** — recovery is a governed state transition, not an
   automatic production activation.

This is research-informed architecture, not a claim of certification.

## Evidence binding

Each incident should be persisted alongside:

- incident digest
- runtime decision digest
- release/code revision
- policy evidence bundle digest
- delegation/audit references where applicable
- rollback artifact reference
- revalidation/TEVV reference
- accountable approval reference

This creates a traceable path from runtime signal to containment and recovery.
